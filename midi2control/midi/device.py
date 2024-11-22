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

        if midi_maps:
            for map in midi_maps:
                self.add_map(map)

    def monitor_inputs(self):
        for msg in self.inport:
            logging.debug(msg)
            for map_name, m in self.midi_maps.items():
                if msg.type == m.type:
                    if msg.channel in flatten(m.channel):
                        if ((msg.type == 'control_change' and msg.control in flatten(m.control))
                                or (msg.type == 'note_on' and msg.note in flatten(m.note))):
                            m.message(self, msg)

    def add_map(self, map):
        self.midi_maps[map.name] = map

    def animate(self):
        pass  # trn on light x, turn off light y, sleep etc.. Example of having key accessible midi_mappings

