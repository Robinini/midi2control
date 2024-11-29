import logging
import subprocess
import mido
import os
import math

from midi2control import notify_user


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
        """
        :param name: Name used as midi device name to connect
        :param midi_maps: List of mappings in dictionary keyed by mode name
        """

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
            self.add_maps(midi_maps)

    def radio(self, map):
        if map.radio is not None:
            for m in self.midi_maps.get(self.mode).values():
                if m != map and m.radio == map.radio:
                    m.off(map, self)

    def monitor_inputs(self):
        for msg in self.inport:
            logging.debug(msg)
            for map_name, m in self.midi_maps.get(self.mode).items():
                if m.type is None or m.type == msg.type:
                    if m.channel is None or msg.channel in flatten(m.channel):
                        if ((msg.type == 'control_change' and (m.control is None or msg.control in flatten(m.control)))
                                or (msg.type == 'note_on' and (m.note is None or msg.note in flatten(m.note)))):
                            m.message(self, msg)

    def add_maps(self, midi_maps):
        for mode, maps in midi_maps.items():
            for map in maps:
                self.add_map(map, mode)
        
    
    def add_map(self, map, mode=None):
        if mode not in self.midi_maps:
            self.midi_maps[mode] = dict()
        self.midi_maps[mode][map.name] = map

    def get_map(self, map_name, mode=None):
        return self.midi_maps[mode][map_name]

    def get_mode_key(self, integer):
        """Calculates suitable rolling index from mode names,
        taking into account -ve numbers and indexes larger than the list"""

        modes = list(self.midi_maps.keys())
        mode_name = modes[integer % len(modes)]

        return mode_name

    def browse_mode(self, map, device=None, msg=None):
        """"""
        mode_key = self.get_mode_key(map.current_state)

        if mode_key != self.mode:
            subject, message = f"MIDI Controller {self.name}", f" mode '{(mode_key or 'DEFAULT')}' ready for selection"
        else:
            subject, message = f"MIDI Controller {self.name}", f"current mode {(self.mode or 'DEFAULT')}"

        logging.info(subject + ' ' + message)
        notify_user(subject, message)

    def change_mode(self, mode_key=None, mode_index=None):
        """

        :param mode: Mode (dict key) to change to
        :param index: Mode as index integer when mode keys are listed
        :return:
        """

        if isinstance(mode_index, int):
            mode_key = self.get_mode_key(mode_index)

        if mode_key in self.midi_maps:
            if mode_key != self.mode:
                self.mode = mode_key
                # Provide user feedback
                self.animate()
                subject, message = f"MIDI Controller {self.name}", f"changed to mode {(self.mode or 'DEFAULT')}"
            else:
                subject, message = f"MIDI Controller {self.name}", f"current mode {(self.mode or 'DEFAULT')}"

        else:
            raise ValueError(f'Invalid mode {mode_key} selected!!')

        logging.info(subject + ' ' + message)
        notify_user(subject, message)

    def animate(self):
        pass

