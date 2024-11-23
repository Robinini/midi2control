import logging
import mido


def flatten(something):
    if isinstance(something, (list, tuple, set, range)):
        for sub in something:
            yield from flatten(sub)
    else:
        yield something

def read_midi_devices():
    inputs = mido.get_input_names()
    outputs = mido.get_output_names()
    logging.debug(inputs)
    logging.debug(outputs)
    return inputs, outputs


def open_input(device_name):
    return mido.open_input(device_name)

def open_output(device_name):
    return mido.open_output(device_name)


class Device:
    def __init__(self, name, midi_maps=None):

        self.name = name
        if self.name not in read_midi_devices()[0]:
            for candidate in read_midi_devices()[0]:
                if candidate.startswith(self.name):
                    logging.warning(f'Device name {self.name} not found, using {candidate}')
                    self.name = candidate
                    break

        self.inport = open_input(self.name)
        self.outport = open_output(self.name)

        self.midi_maps = dict()  # Accessible using keys
        self.mode = None

        if midi_maps:
            for mode, maps in midi_maps.items():
                for map in maps:
                    self.add_map(map, mode)

    def monitor_inputs(self):
        for msg in self.inport:
            logging.debug(msg)
            for map_name, m in self.midi_maps.get(self.mode).items():
                if msg.type == m.type:
                    if msg.channel in flatten(m.channel):
                        if ((msg.type == 'control_change' and msg.control in flatten(m.control))
                                or (msg.type == 'note_on' and msg.note in flatten(m.note))):
                            m.message(self, msg)

    def add_map(self, map, mode=None):
        if mode not in self.midi_maps:
            self.midi_maps[mode] = dict()
        self.midi_maps[mode][map.name] = map

    def change_mode(self, mode=None, index=None):
        """

        :param mode: Mode (dict key) to change to
        :param index: Mode as index integer when mode keys are listed
        :return:
        """
        print('Changing to mode', mode, index)
        # ToDo: think thrg and implement.
        #  Attach to browser or try changing using this method and a key.
        #  Catch errors Provied used (os Notification feedback based on Win/Linus/?)
        #  Each mode has anmation callback (future)?


    def animate(self):
        raise NotImplementedError

