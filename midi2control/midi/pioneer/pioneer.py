import logging
from midi2control.midi.map import MidiMap


class JogDial(MidiMap):
    def __init__(self, name, channel, control, description=None, invert=False, max=None, min=None):
        """

        :param max: Maximum output limit
        :param min: Minimum output limit
        """

        typ = 'control_change'

        MidiMap.__init__(self, name=name, typ=typ, channel=channel, control=control, description=description)

        self.invert = invert
        self.max = max
        self.min = min

        self.reset()

    def reset(self):
        MidiMap.reset(self)
        self.current_state = 0  # 0 is center 1.0 is full revolution (+ is clockwise)

    def message(self, device, msg):
        calculated_position = self.current_state + ((msg.value - 64) / 720)
        if self.max is not None and calculated_position > self.max:
            calculated_position = self.max
        if self.min is not None and calculated_position < self.min:
            calculated_position = self.min
        self.current_state = -calculated_position if self.invert else calculated_position
        logging.debug(self.current_state)
        self.output(device, msg)


class Slide(MidiMap):
    def __init__(self, name, channel, control, description=None, invert=False, center=False):
        """
        :param min: What the minimum value should map to
        :param max: What the minimum value should map to
        """

        typ = 'control_change'

        MidiMap.__init__(self, name=name, typ=typ, channel=channel, control=control, description=description)

        self.invert = invert
        self.center = center

        self.coarse_control = control[0]
        self.fine_control = control[1]

        self.coarse_value = None
        self.fine_value = None

        self.reset()

    def reset(self):
        MidiMap.reset(self)
        self.current_state = 1 if self.invert else 0

    def message(self, device, msg):
        print('here')
        if msg.control == self.coarse_control:
            self.coarse_value = msg.value
        elif msg.control == self.fine_control:
            self.fine_value = msg.value
        if self.coarse_value is not None and self.fine_value is not None:
            calculated_position = (self.coarse_value * 128 + self.fine_value) / 16383
            if self.invert:
                calculated_position = 1 - calculated_position
            if self.center:
                calculated_position = calculated_position - 0.5
            self.current_state = calculated_position
        logging.debug(self.current_state)
        self.output(device, msg)


class Rotate(Slide):
    def __init__(self, name, channel, control, description=None, invert=False, center=False):
        """ Clone of slide. Functionally the same, but named to match Pioneer terminology"""
        Slide.__init__(self, name=name, channel=channel, control=control, description=description, invert=invert, center=center)


class Press(MidiMap):
    def __init__(self, name, channel, note, feedback=None, toggle=False, description=None):

        typ = 'note_on'

        MidiMap.__init__(self, name=name, typ=typ, channel=channel, note=note, description=description)

        self.reset()

    def reset(self):
        pass

    def message(self, device, msg):
        if msg.velocity == 127:
            self.current_state = True
        elif msg.velocity == 0:
            self.current_state = False
        logging.debug(self.current_state)  # also, react?
        self.output(device, msg)

    def feedback(self, device, msg):
        device.outport.send(msg)  # Echo same message back



class Toggle(Press):
    def __init__(self, name, channel, note, feedback=None, description=None):
        Press.__init__(self, name=name, channel=channel, note=note, feedback=feedback, description=description)

    def message(self, device, msg):
        print(msg.velocity, self.current_state)
        if msg.velocity == 127:
            if self.current_state is None:
                self.current_state = True
            self.current_state = not self.current_state
        print(msg.velocity, self.current_state)

        logging.debug(self.current_state)
        self.output(device, msg)

    def feedback(self, device, msg):
        msg.velocity = 127 if self.current_state else 0
        device.outport.send(msg)  # Echo message but with correct velocity

