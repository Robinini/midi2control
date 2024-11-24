from midi2control.midi.map import MidiMap
from midi2control.midi.device import flatten
import mido


class JogDial(MidiMap):

    typ = 'control_change'

    def __init__(self, name, channel, control, description=None, invert=False, max_out=None, min_out=None):
        """

        :param max: Maximum output limit
        :param min: Minimum output limit
        """

        MidiMap.__init__(self, name=name, typ=self.typ, channel=channel, control=control, description=description)

        self.invert = invert
        self.max = max_out
        self.min = min_out

        self.reset()

    def reset(self, state=None):
        MidiMap.reset(self, 0) # 0 is center 1.0 is full revolution (+ is clockwise)

    def message(self, device, msg):
        scaled_value = (msg.value - 64) / 720
        if self.invert:
            scaled_value = -1 *  scaled_value
        calculated_position = self.current_state + scaled_value
        if self.max is not None and calculated_position > self.max:
            calculated_position = self.max
        if self.min is not None and calculated_position < self.min:
            calculated_position = self.min
        self.current_state = calculated_position
        self.output(device, msg)


class Browser(MidiMap):

    typ = 'control_change'

    def __init__(self, name, channel, control, description=None, invert=False):
        """
        Current position as integer + / - from 0 depending on clock-/anticlockwise
        """

        MidiMap.__init__(self, name=name, typ=self.typ, channel=channel, control=control, description=description)

        self.invert = invert

        self.reset()

    def reset(self, state=None):
        MidiMap.reset(self, 0) # 0 is center

    def message(self, device, msg):
        if msg.value < 98:  # Clockwise
            self.current_state += -msg.value if self.invert else msg.value
        else:
            self.current_state += (128-msg.value) if self.invert else -(128-msg.value)
        self.output(device, msg)


class Slide(MidiMap):

    typ = 'control_change'

    def __init__(self, name, channel, control, description=None, invert=False, center=False):
        """
        :param min: What the minimum value should map to
        :param max: What the minimum value should map to
        :param control: Tuple pair of course and fine controls, or list of control pair tuples. Cannot be None
        """

        MidiMap.__init__(self, name=name, typ=self.typ, channel=channel, control=control, description=description)

        self.invert = invert
        self.center = center

        # Create list of corresponding coarse and fine control values
        self.coarse_control = [control[0] for control in control] if isinstance(control, list) else [control[0]]
        self.fine_control = [control[1] for control in control] if isinstance(control, list) else [control[1]]

        self.coarse_value = None
        self.fine_value = None

        self.reset()

    def reset(self, state=0):
        MidiMap.reset(self, (1 - state) if self.invert else state)
        self.coarse_value = None
        self.fine_value = None

    def message(self, device, msg):
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

            self.current_state = calculated_position
            # Reset values
            self.coarse_value = None
            self.fine_value = None
        self.output(device, msg)


class Rotate(Slide):
    def __init__(self, name, channel, control, description=None, invert=False, center=False):
        """ Clone of slide. Functionally the same, but named to match Pioneer terminology"""
        Slide.__init__(self, name=name, channel=channel, control=control, description=description, invert=invert, center=center)


class Press(MidiMap):

    typ = 'note_on'

    def __init__(self, name, channel, note, feedback=None, toggle=False, description=None):

        MidiMap.__init__(self, name=name, typ=self.typ, channel=channel, note=note, description=description)

        self.feedback = feedback
        self.toggle = toggle
        self.reset()

    def reset(self, state=False):
        MidiMap.reset(self, state)

    def message(self, device, msg):
        if msg.velocity == 127:
            if self.toggle:
                if self.current_state is not True:
                    self.current_state = True
                    self.led_on(device)
                else:
                    self.current_state = False
                    self.led_off(device)
            else:
                self.current_state = True
                self.led_on(device)
        elif msg.velocity == 0 and not self.toggle:
            self.current_state = False
            self.led_off(device)
        self.output(device, msg)

    def led_on(self, device):
        for channel in flatten( self.channel):
            for note in flatten(self.note):
                device.outport.send(mido.Message('note_on', channel=channel, note=note, velocity=127))

    def led_off(self, device):
        for channel in flatten( self.channel):
            for note in flatten(self.note):
                device.outport.send(mido.Message('note_on', channel=channel, note=note, velocity=0))




