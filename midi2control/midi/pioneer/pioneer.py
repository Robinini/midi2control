import logging
from midi2control.midi.mapping import MidiMap
from midi2control.midi.device import flatten
import mido


class JogDial(MidiMap):

    typ = 'control_change'

    def __init__(self, name, channel, control, description=None, outputs=None, invert=False, max_state=None,
                 min_state=None, initial_state=0):
        """

        DK-Deck Jog-dial control input.
        N.b: Sides and top of deck may be differnt cahnnels.

        :param name: (str) Name used to refer or access the mapping
        :param channel: (int) MIDI channel, iterable of channels or None for all channels
        :param control: Tuple pair of course and fine controls, or list of control pair tuples
        :param outputs: List of mapping output functions which should be executed on mapping input
        :param description: (str) Detailed description of the mapping
        :param invert: (bool) if False, clockwise increases the state, if True, clockwise will reduce the state value
        :param max_state: Limit current_state to this maximum value
        :param min_state: Limit current_state to this minimum value
        :param initial_state: 0 is center 1.0 is full revolution (+ is clockwise)
        """

        super().__init__(name=name, typ=self.typ, channel=channel, control=control, outputs=outputs,
                         description=description, initial_state=initial_state)

        self.invert = invert
        self.max_state = max_state
        self.min_state = min_state

        self.reset()
        self.output()

    def reset(self):
        """
        Reset the current_state to the initial_state
        :return: None
        """
        super().reset()

    def message(self, device, msg):
        """
        handle a matching MIDI message

        :param device: midi.device Device associated with this mapping
        :param msg: mido message received from the device
        """
        scaled_value = (msg.value - 64) / 720
        if self.invert:
            scaled_value = -1 *  scaled_value
        calculated_position = self.current_state + scaled_value
        if self.max_state is not None and calculated_position > self.max_state:
            calculated_position = self.max_state
        if self.min_state is not None and calculated_position < self.min_state:
            calculated_position = self.min_state
        self.set(calculated_position)
        self.output(device, msg)


class Browser(MidiMap):

    typ = 'control_change'

    def __init__(self, name, channel, control, description=None, outputs=None, invert=False):
        """

        Manages current position as integer + / - from 0 depending on clock-/anticlockwise

        :param name: (str) Name used to refer or access the mapping
        :param channel: (int) MIDI channel, iterable of channels or None for all channels
        :param control: (int) MIDI control, iterable of controls or None for all controls
        :param description: (str) Detailed description of the mapping
        :param outputs: List of mapping output functions which should be executed on mapping input
        :param invert: (bool) if False, clockwise increases the state, if True, clockwise will reduce the state value
        :param outputs: List of mapping output functions which should be executed on mapping input

        """

        super().__init__(name=name, typ=self.typ, channel=channel, control=control, description=description,
                         outputs=outputs, initial_state=0)

        self.invert = invert

        self.reset()
        self.output()

    def reset(self):
        """
        Reset the current_state to the initial_state
        :return: None
        """
        super().reset()

    def message(self, device, msg):
        """
        handle a matching MIDI message

        :param device: midi.device Device associated with this mapping
        :param msg: mido message received from the device
        """
        if msg.value < 98:  # Clockwise
            self.set(self.current_state + (-msg.value if self.invert else msg.value))
        else:
            self.set(self.current_state + ((128-msg.value) if self.invert else -(128-msg.value)))
        self.output(device, msg)


class Slide(MidiMap):

    typ = 'control_change'

    def __init__(self, name, channel, control, description=None, outputs=None, invert=False, center=False, step=None):
        """

        :param name: (str) Name used to refer or access the mapping
        :param channel: (int) MIDI channel, iterable of channels or None for all channels
        :param control: Tuple pair of course and fine controls, or list of control pair tuples
        :param description: (str) Detailed description of the mapping
        :param outputs: List of mapping output functions which should be executed on mapping input
        :param invert: (bool) if False, clockwise increases the state, if True, clockwise will reduce the state value
        :param center: If True, center position of slider is set to 0 (with +1 and -1 at extents).
        :param step: Difference between self.previous_state and self.current_state, above which outputs will be triggered
        """

        MidiMap.__init__(self, name=name, typ=self.typ, channel=channel, control=control,
                         description=description, outputs=outputs, initial_state=1 if invert else 0)

        self.invert = invert
        self.center = center
        self.step = step

        # Create list of corresponding coarse and fine control values
        self.coarse_control = [control[0] for control in control] if isinstance(control, list) else [control[0]]
        self.fine_control = [control[1] for control in control] if isinstance(control, list) else [control[1]]

        self.coarse_value = None
        self.fine_value = None

        self.reset()
        self.output()

    def reset(self):
        """
        Reset the current_state to the initial_state
        :return: None
        """
        super().reset()
        self.coarse_value = None
        self.fine_value = None

    def message(self, device, msg):
        """
        handle a matching MIDI message

        :param device: midi.device Device associated with this mapping
        :param msg: mido message received from the device
        """
        if msg.control in self.coarse_control:
            self.coarse_value = msg.value
        elif msg.control in self.fine_control:
            self.fine_value = msg.value
        if self.coarse_value is not None and self.fine_value is not None:  # Both have been sent

            calculated_position = (self.coarse_value * 128 + self.fine_value) / 16383
            if self.invert:
                calculated_position = 1 - calculated_position
            if self.center:
                calculated_position = 2 * (calculated_position - 0.5)

            # Reset values
            self.coarse_value = None
            self.fine_value = None

            # Update value and output if above step value (or no step)
            if not self.step or abs(calculated_position - self.current_state) > self.step or calculated_position in (0, 1):
                self.set(calculated_position)
                self.output(device, msg)
            else:
                logging.debug(f'{self} output change below step value, outputs not executed')


class Rotate(Slide):
    """
    Clone of Slide. Functionally the same, but named to match Pioneer terminology
    """
    def __init__(self, name, channel, control, description=None, outputs=None, invert=False, center=False, step=None):
        Slide.__init__(self, name=name, channel=channel, control=control, description=description, outputs=outputs,
                       invert=invert, center=center, step=step)


class Press(MidiMap):

    typ = 'note_on'

    def __init__(self, name, channel, note, toggle=False, description=None, outputs=None, radio=None, initial_state=False):
        """
        PAD button. Can also have built-in LED to provide user feedback.

        :param name: (str) Name used to refer or access the mapping
        :param channel: (int) MIDI channel, iterable of channels or None for all channels
        :param note: (int) MIDI note, iterable of note or None for all note
        :param toggle: (bool) IF True, button will remain on till next pressed (or radio group deselected)
        :param description: (str) Detailed description of the mapping
        :param outputs: List of mapping output functions which should be executed on mapping input
        :param initial_state: Initial value of the control (True/False/float)
        :param radio: (str) Name of group if considered a radio button (activation of member resets other members)

        """

        super().__init__(name=name, typ=self.typ, channel=channel, note=note,
                         description=description, outputs=outputs, radio=radio, initial_state=initial_state)

        self.toggle = toggle

        self.reset()
        self.output()

    def reset(self):
        """
        Reset the current_state to the initial_state
        :return: None
        """
        super().reset()

    def message(self, device, msg):
        """
        handle a matching MIDI message

        :param device: midi.device Device associated with this mapping
        :param msg: mido message received from the device
        """
        if msg.velocity == 127:
            if self.radio is not None:
                if self.current_state is not True:
                    self.on(self, device, msg)
            elif self.toggle:
                if self.current_state is not True:
                    self.on(self, device, msg)
                else:
                    self.off(self, device, msg)
            else:
                self.on(self, device, msg)
        elif msg.velocity == 0 and not self.toggle and not self.radio:
            self.off(self, device, msg)


    def on(self, mapping, device=None, msg=None):
        """
        Turn button on - providing LED feedback.

        This accepts parameters consistent with output mappings to allow this method to be the output of another method

        :param mapping: midi.mapping MidiMap based object triggering this method
        :param device: midi.device Device associated with this mapping (unused)
        :param msg: mido message received from the device (unused)
        :return: None
        """
        """ nb: Can be called by other maps, eg: Group radio button or multiselect"""
        if self.current_state is not True:
            self.set(True)
            self.led_on(device)
            if self.radio is not None:
                device.radio(self)
            self.output(device, msg)

    def off(self, mapping, device=None, msg=None):
        """
        Turn button off - providing LED feedback.

        This accepts parameters consistent with output mappings to allow this method to be the output of another method

        :param mapping: midi.mapping MidiMap based object triggering this method
        :param device: midi.device Device associated with this mapping (unused)
        :param msg: mido message received from the device (unused)
        :return: None
        """

        if self.current_state is not False:
            self.set(False)
            if mapping != self:
                logging.debug(f'{self} turned off by {mapping}')
            self.led_off(device)
            self.output(device, msg)

    def led_on(self, device):
        """
        Turn the button LED o using the outgoing MIDI channel to the device

        :param device: midi.device Device to send to
        :return: None
        """
        for channel in flatten(self.channel):
            for note in flatten(self.note):
                device.outport.send(mido.Message('note_on', channel=channel, note=note, velocity=127))

    def led_off(self, device):
        """
        Turn the button LED o using the outgoing MIDI channel to the device

        :param device: midi.device Device to send to
        :return: None
        """
        for channel in flatten( self.channel):
            for note in flatten(self.note):
                device.outport.send(mido.Message('note_on', channel=channel, note=note, velocity=0))




