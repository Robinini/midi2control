import logging
import mido
import time


from midi2control import notify_user
from midi2control.midi.mapping import MidiMap


def flatten(something):
    if isinstance(something, (list, tuple, set, range)):
        for sub in something:
            yield from flatten(sub)
    else:
        yield something

def read_midi_devices():
    try:
        inputs = mido.get_input_names()
        outputs = mido.get_output_names()
    except Exception as e:
        print(e)
        return list(), list()
    return inputs, outputs


def open_input(device_name):
    return mido.open_input(device_name)

def open_output(device_name):
    return mido.open_output(device_name)


class Device:
    def __init__(self, name, device_name=None, midi_maps=None, timeout=None, wait=5):
        """
        :param name: Name used as midi device name to connect
        :param midi_maps: List of mappings in dictionary keyed by mode name
        """

        self.name = name
        self.device_name = device_name or name
        self.timeout = timeout
        self.wait = wait
        self.inport = None
        self.outport = None

        self.connect()

        self.midi_maps = dict()  # Accessible using keys
        self.mode = None

        if midi_maps:
            self.add_maps(midi_maps)

    def __str__(self):
        return f'{self.name} [{self.device_name}]'

    def connect(self):
        start_time = time.time()
        while not self.timeout or time.time() - start_time <= self.timeout:
            if self.device_name in read_midi_devices()[0]:
                self.inport = open_input(self.device_name)
                self.outport = open_output(self.device_name)
                logging.info(f'Device {self} connected')
                return
            else:
                for candidate in read_midi_devices()[0]:
                    if candidate.startswith(self.device_name) or candidate.startswith(self.name):
                        logging.warning(f'Device name {self.device_name} not found, using {candidate}')
                        self.device_name = candidate
                        self.inport = open_input(self.device_name)
                        self.outport = open_output(self.device_name)
                        logging.info(f'Device {self} connected')
                        return
            logging.warning(f'Device {self} not found, waiting {self.wait} seconds')
            time.sleep(self.wait)

        raise TimeoutError(f'Device {self} not found')

    def radio(self, mapping):
        if mapping.radio is not None:
            for m in self.midi_maps.get(self.mode).values():
                if m != mapping and m.radio == mapping.radio:
                    m.off(mapping, self)

    def monitor_inputs(self):
        while True:
            if self.device_name not in read_midi_devices()[0]:
                self.connect()

            for msg in self.inport.iter_pending():
                logging.debug(msg)
                for map_name, m in self.midi_maps.get(self.mode).items():
                    if m.type is None or m.type == msg.type:
                        if m.channel is None or msg.channel in flatten(m.channel):
                            if ((msg.type == 'control_change' and (m.control is None or msg.control in flatten(m.control)))
                                    or (msg.type == 'note_on' and (m.note is None or msg.note in flatten(m.note)))):
                                m.message(self, msg)

    def add_maps(self, midi_maps):
        for mode, maps in midi_maps.items():
            for mapping in maps:
                self.add_map(mapping, mode)
    
    def add_map(self, mapping, mode=None):
        if mode not in self.midi_maps:
            self.midi_maps[mode] = dict()
        self.midi_maps[mode][mapping.name] = mapping

    def get_map(self, map_name, mode=None):
        return self.midi_maps[mode][map_name]

    def get_mode_key(self, integer):
        """Calculates suitable rolling index from mode names,
        taking into account -ve numbers and indexes larger than the list"""

        modes = list(self.midi_maps.keys())
        mode_name = modes[integer % len(modes)]

        return mode_name

    def browse_mode(self, mapping, device=None, msg=None):
        """"""
        mode_key = self.get_mode_key(mapping.current_state)

        if mode_key != self.mode:
            subject, message = f"MIDI Controller {self}", f" mode '{(mode_key or 'DEFAULT')}' ready for selection"
        else:
            subject, message = f"MIDI Controller {self}", f"current mode {(self.mode or 'DEFAULT')}"

        logging.info(subject + ' ' + message)
        notify_user(subject, message)

    def change_mode(self, mode_key=None, mode_index=None):
        """

        :param mode_key: Mode (dict key) to change to
        :param mode_index: Mode as index integer when mode keys are listed
        :return:
        """

        # Obtain current_state if the index source is a Map based object
        if MidiMap in mode_index.__class__.__mro__:
            mode_index = int(mode_index.current_state)
        # Use index to get mode_key
        if isinstance(mode_index, int):
            mode_key = self.get_mode_key(mode_index)

        # Use provided or derived mode_key to change mode
        if mode_key in self.midi_maps:
            if mode_key != self.mode:
                self.mode = mode_key
                # Provide user feedback
                self.animate()
                subject, message = f"MIDI Controller {self}", f"changed to mode {(self.mode or 'DEFAULT')}"
            else:
                subject, message = f"MIDI Controller {self}", f"current mode {(self.mode or 'DEFAULT')}"

        else:
            raise ValueError(f'Invalid mode {mode_key} selected!!')

        logging.info(subject + ' ' + message)
        notify_user(subject, message)

    def animate(self):
        pass

