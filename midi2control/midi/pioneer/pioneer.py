import logging
from midi2control.midi.map import MidiMap
import mido


class JogDial(MidiMap):

    typ = 'control_change'

    def __init__(self, name, channel, control, description=None, invert=False, max=None, min=None):
        """

        :param max: Maximum output limit
        :param min: Minimum output limit
        """

        MidiMap.__init__(self, name=name, typ=self.typ, channel=channel, control=control, description=description)

        self.invert = invert
        self.max = max
        self.min = min

        self.reset()

    def reset(self):
        MidiMap.reset(self, 0) # 0 is center 1.0 is full revolution (+ is clockwise)

    def message(self, device, msg):
        calculated_position = self.current_state + ((msg.value - 64) / 720)
        if self.max is not None and calculated_position > self.max:
            calculated_position = self.max
        if self.min is not None and calculated_position < self.min:
            calculated_position = self.min
        self.current_state = -calculated_position if self.invert else calculated_position
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

    def reset(self):
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
        """

        MidiMap.__init__(self, name=name, typ=self.typ, channel=channel, control=control, description=description)

        self.invert = invert
        self.center = center

        self.coarse_control = control[0]
        self.fine_control = control[1]

        self.coarse_value = None
        self.fine_value = None

        self.reset()

    def reset(self):
        MidiMap.reset(self, 1 if self.invert else 0)

    def message(self, device, msg):
        if msg.control == self.coarse_control:
            self.coarse_value = msg.value
        elif msg.control == self.fine_control:
            self.fine_value = msg.value
        if self.coarse_value is not None and self.fine_value is not None:
            calculated_position = (self.coarse_value * 128 + self.fine_value) / 16383
            if self.invert:
                calculated_position = 1 - calculated_position
            if self.center:
                calculated_position = 2 * (calculated_position - 0.5)
            self.current_state = calculated_position
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

    def reset(self):
        MidiMap.reset(self, False)

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
        # ToDo - what msg/data to send?
        device.outport.send(mido.Message('note_on', channel=self.channel, note=self.feedback, velocity=127))

    def led_off(self, device):
        # ToDo - what msg/data to send?
        device.outport.send(mido.Message('note_on', channel=self.channel, note=self.feedback, velocity=0))




