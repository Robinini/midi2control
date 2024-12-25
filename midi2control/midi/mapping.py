import logging
import copy

"""
Mappings to associate with a device control (MIDI signal)

"""

def map_copy(maps):
    """
    Copies a mapping or list of mappings.

    This allows the user to copy and modify the mapping without affecting the
    original.

    :param maps: MidiMap or list of MidiMap instances
    :return: Copy of the MidiMap or list of MidiMap instances
    """
    return [copy.deepcopy(m) for m in maps] if isinstance(maps, list) else copy.deepcopy(maps)


class MidiMap:
    def __init__(self, name, typ=None, channel=None, control=None, note=None, outputs=None, description=None,
                 initial_state=None, radio=None):
        """
        Mapping. NB This could be attached to multiple devices attached in parallel

        If the typ, channel control or note is None, all messages which satisfy the other criteria will
        trigger the outputs.

        :param name: (str) Name used to refer or access the mapping
        :param typ: (str) MIDI message type or None for all types. Eg: 'note_on'
        :param channel: (int) MIDI channel, iterable of channels or None for all channels
        :param control: (int) MIDI control, iterable of controls or None for all controls
        :param note: (int) MIDI note, iterable of notes or None for all notes
        :param outputs: List of mapping output functions which should be executed on mapping input
        :param description: (str) Detailed description of the mapping
        :param initial_state: Initial value of the control (True/False/float)
        :param radio: (str) Name of group if considered a radio button (activation of member resets other members)
        """
        self.name = name  # unique for device
        self.description = description

        self.type = typ
        self.channel = channel
        self.control = control
        self.note = note

        self.radio = radio

        self.outputs = outputs or list()

        self.initial_state = initial_state
        self.previous_state = initial_state
        self.current_state = initial_state

        logging.debug(f'Created mapping {self.name} {f"({self.description})" if self.description else str()}')

    def __str__(self):
        """
        String representation magic method
        :return: String
        """
        return f"{self.__class__.__name__}, {self.name}, {self.current_state}"

    def set(self, state):
        """
        Set state of mapping to a new value
        :param state: New current_state
        :return: None
        """
        logging.debug(f'Setting {self} to {state}')
        self.previous_state = self.current_state
        self.current_state = state
        logging.debug(f'Set {self} from {self.previous_state} to {self.current_state}')

    def reset(self):
        """
        Reset the current_state to the initial_state
        :return: None
        """
        logging.debug(f'Resetting {self}')
        self.set(self.initial_state)
        logging.debug(f'Reset {self}')

    def on(self, mapping, device=None, msg=None):
        """
        Abstract method to turn the mapping 'on'

        :param mapping: midi.mapping MidiMap based object triggering ths method
        :param device: midi.device Device associated with this mapping
        :param msg: mido message received from the device
        """
        raise NotImplementedError

    def off(self, mapping, device=None, msg=None):
        """
        Abstract method to turn the mapping 'off'

        :param mapping: midi.mapping MidiMap based object triggering ths method
        :param device: midi.device Device associated with this mapping
        :param msg: mido message received from the device
        """
        raise NotImplementedError

    def message(self, device, msg):
        """
        Abstract method to handle a matching MIDI message

        :param device: midi.device Device associated with this mapping
        :param msg: mido message received from the device
        """
        self.output(device, msg)

    def add_output(self, func, initialise=True):
        """
        Add an output function to execute when message received
        :param func: function which accepts 3 arguments: mapping object, device (may be None) and message (may be None)
        :param initialise: (bool) Whether to trigger the output after adding it
        :return: self to allow method chaining
        """
        self.outputs.append(func)
        # Initiate output with current value
        if initialise:
            func(self)

        return self

    def output(self, device=None, msg=None):
        """
        Trigger all configured output functions

        :param device: midi.device Device associated with this mapping
        :param msg: mido message received from the device
        :return:
        """
        logging.info(f'{self} from Device {device if device else "(no device)"} '
                     f'triggered by message {msg or "(no message)"}')
        for output in self.outputs:
            output(self, device, msg)
