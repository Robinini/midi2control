import logging
import time
import mido

from midi2control import notify_user
from midi2control.midi.mapping import MidiMap


"""
Base MIDI device.

"""

def flatten(something):
    """
    Flatten a multilevel list or item

    :param something: Iterable of any object
    :return: Flattened list
    """
    if isinstance(something, (list, tuple, set, range)):
        for sub in something:
            yield from flatten(sub)
    else:
        yield something

def read_midi_devices():
    """
    Obtain all connected MIDI devices

    :return: list of input devices, list of output devices
    """
    try:
        inputs = mido.get_input_names()
        outputs = mido.get_output_names()
    except Exception as e:
        print(e)
        return list(), list()
    return inputs, outputs


def open_input(device_name):
    """
    Open a MIDI device as an input

    :param device_name: (str) expected device name eg: 'PIONEER DDJ-SB:PIONEER'
    :return: Mido input device connection
    """
    return mido.open_input(device_name)

def open_output(device_name):
    """
    Open a MIDI device as an output

    :param device_name: (str) expected device name eg: 'PIONEER DDJ-SB:PIONEER'
    :return: Mido output device connection
    """
    return mido.open_output(device_name)


class Device:
    def __init__(self, name, device_name=None, midi_maps=None, timeout=None, wait=5):
        """
        MIDI device basic class. Can be extended for specific manufacturers or products

        :param name: (str) Name of device
        :param device_name: (str) Name of device according to mido device connection (defaults to name)
        :param midi_maps: Dict of Lists of midi.mapping MidiMap instances (keyed by mode name)
        to use with this device (can be added later wth the methods add_maps or add_map)
        :param timeout: (int) Seconds to wait for device connection or None if it should wait indefinitely
        :param wait: Seconds to wait before reattempting (re)connection
        """

        self.name = name
        self.device_name = device_name or name
        self.timeout = timeout
        self.wait = wait
        self.inport = None
        self.outport = None

        self.connect()

        self.midi_maps = dict()  # Accessible using keys
        self.mode = None  # ToDo: What if the user has just named modes?

        if midi_maps:
            self.add_maps(midi_maps)

    def __str__(self):
        """
        String representation magic method
        :return: String
        """
        return f'{self.name} [{self.device_name}]'

    def connect(self):
        """
        Connect to physical MIDI device. If the explicit device_name is not found, will connect to the first device
        starting with the device_name. This can be useful if the device name is based on the model
        but is also appended with usb connection details

        :return: None
        """
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
        """
        Change states of all mappings in a group. None initiating mappings will be set to the opposite

        #ToDO: What if initiating mapping is set to False - do others all get set to True?

        :param mapping: Initiating midi.mapping MidiMap instance
        :return: None
        """
        if mapping.radio is not None:
            for m in self.midi_maps.get(self.mode).values():
                if m != mapping and m.radio == mapping.radio:
                    m.off(mapping, self)

    def check_inputs(self):
        """
        Read incoming MIDI messages - reconnecting if required

        :return: None
        """

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

    def monitor_inputs(self):
        """
        Blocking method to continually check for MIDI messages from device

        :return: None
        """
        while True:
            self.check_inputs()

    def add_maps(self, midi_maps):
        """
        Add midi.mapping MidiMap instances

        :param midi_maps: dict of lists of midi.mapping MidiMap instances (keyed by mode name)
        :return: None
        """
        for mode, maps in midi_maps.items():
            for mapping in maps:
                self.add_map(mapping, mode)
    
    def add_map(self, mapping, mode=None):
        """
        Add midi.mapping MidiMap instance to a mode.

        :param mapping: midi.mapping MidiMap instance
        :param mode: Mode name or None for default mode
        :return: None
        """
        if mode not in self.midi_maps:
            self.midi_maps[mode] = dict()
        self.midi_maps[mode][mapping.name] = mapping

    def get_map(self, map_name, mode=None):
        """
        Access a midi.mapping MidiMap instance within a mode using the mode name and mapping name

        :param map_name: (str) midi.mapping MidiMap instance name
        :param mode: Mode name or None for default mode
        :return: midi.mapping MidiMap instance
        """
        return self.midi_maps[mode][map_name]

    def get_mode_key(self, integer):
        """
        Calculates suitable rolling index from mode names,
        taking into account -ve numbers and indexes larger than the list

        :param integer: (int)
        :return: Mode name
        """

        modes = list(self.midi_maps.keys())
        mode_name = modes[integer % len(modes)]

        return mode_name

    def browse_mode(self, mapping, device=None, msg=None):
        """
        Device method which can be passed as an output mapping function to a file selector knob.

        This allows the control to preselect ('cue' up) the next mode. The next mode can then be selected
        by with the device method change_mode() which can be attached to an output button.

        Example use:
        browser = ddj.get_map('BROWSE:ROTATE')
        browser.add_output(ddj.browse_mode)
        ddj.get_map('BROWSE:PRESS').add_output(output(ddj.change_mode, mode_index=browser))

        :param mapping: midi.mapping MidiMap based object triggering ths method
        :param device: midi.device Device associated with this mapping (unused)
        :param msg: mido message received from the device (unused)
        :return: None
        """

        mode_key = self.get_mode_key(mapping.current_state)

        if mode_key != self.mode:
            subject, message = f"MIDI Controller {self}", f" mode '{(mode_key or 'DEFAULT')}' ready for selection"
        else:
            subject, message = f"MIDI Controller {self}", f"current mode {(self.mode or 'DEFAULT')}"

        logging.info(subject + ' ' + message)
        notify_user(subject, message)

    def change_mode(self, mode_key=None, mode_index=None):
        """
        Changes the current configuration mode to the next selected (or cue'd up) mode
        from the device method.browse_mode()

        Example use:
        browser = ddj.get_map('BROWSE:ROTATE')
        browser.add_output(ddj.browse_mode)
        ddj.get_map('BROWSE:PRESS').add_output(output(ddj.change_mode, mode_index=browser))

        :param mode_key: Mode (dict key) to change to
        :param mode_index: Mode as index integer when mode keys are listed
        :return: None
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
        """
        Abstract method to allow subclass devices to provide some sort of animation using the LED lights for example.
        :return:
        """
        pass

