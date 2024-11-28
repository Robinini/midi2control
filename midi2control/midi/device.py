import logging
import subprocess
import mido
import os
import math

if os.name == 'nt':
    from win10toast import ToastNotifier


def notify_user(subject, message):
    if os.name == 'nt':
        ToastNotifier().show_toast(subject, message, duration=5, threaded=True)
    elif os.name == 'darwin':
        os.system("""osascript -e 'display notification "{}" with title "{}"'""".format(subject, message))
    elif os.name == 'posix':
        subprocess.run(['notify-send', subject, message])


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
        :param midi_maps:
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
            for mode, maps in midi_maps.items():
                for map in maps:
                    self.add_map(map, mode)

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

    def add_map(self, map, mode=None):
        if mode not in self.midi_maps:
            self.midi_maps[mode] = dict()
        self.midi_maps[mode][map.name] = map

    def get_map(self, map_name, mode=None):
        return self.midi_maps[mode][map_name]

    def get_mode_index(self, integer):
        """Calculates suitable rolling index from mode names,
        taking into account -ve numbers and indexes larger than the list"""
        # ToDO
        max_index = len(self.midi_maps.keys()) - 1
        if integer <= max_index:
            return integer

    def browse_mode(self, map, device=None, msg=None):
        """"""
        mode_name = list(self.midi_maps.keys())[self.get_mode_index(map.current_state)]

        subject, message = f"Use MIDI Controller {self.name}", f" mode '{mode_name}'?"
        logging.info(subject, message)
        notify_user(subject, message)

    def change_mode(self, mode_name=None, mode_index=0):
        """

        :param mode: Mode (dict key) to change to
        :param index: Mode as index integer when mode keys are listed
        :return:
        """

        if mode_name is not None:
            self.mode = mode_name
        elif mode_index is not None:
            self.mode = list(self.midi_maps.keys())[self.get_mode_index(mode_index)]

        # Provide user feedback
        self.animate()

        subject, message = f"MIDI Controller {self.name}", f"changing to mode {self.mode}"
        logging.info(subject, message)
        notify_user(subject, message)



    def animate(self):
        pass

