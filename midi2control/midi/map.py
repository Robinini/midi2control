import logging
import copy


def map_copy(maps):
    return [copy.deepcopy(m) for m in maps] if isinstance(map, list) else copy.deepcopy(maps)


class MidiMap:
    def __init__(self, name, typ, channel, control=None, note=None, outputs=None, description=None,
                 initial_state=None, radio=None):
        """
        Mapping. NB This could be attached to multiple devices attached in parallel
        :param name: Name used as midi device name to connect
        :param type: MIDI message type or None for all types
        :param channel: MIDI channel, iterable of channels or None for all channels
        :param control: MIDI control, iterable of controls or None for all controls
        :param outputs: List of map output functions which should be executed on mapping input
        :param description:
        :param radio: Name of group if considered a radio button (activation of member resets other members)
        """
        self.name = name  # unique for device
        self.description = description

        self.type = typ
        self.channel = channel
        self.control = control
        self.note = note

        self.radio = radio

        self.initial_state = initial_state
        self.current_state = initial_state

        self.outputs = outputs or list()

        logging.debug(f'Creating mapping {self.name} {f"({self.description})" if self.description else str()}')

    def __str__(self):
        return f"{self.__class__.__name__}, {self.name}, {self.current_state}"

    def reset(self):
        logging.debug(f'Resetting {self}')
        self.current_state = self.initial_state
        self.output()
        logging.debug(f'Reset {self}')

    def on(self, map, device=None, msg=None):
        raise NotImplementedError

    def off(self, map, device=None, msg=None):
        raise NotImplementedError

    def message(self, device, msg):
        """

        :param msg: mido midi message
        :param controller: Device controller triggering this message
        :return:
        """
        raise NotImplementedError

    def add_output(self, func, initialise=True):
        self.outputs.append(func)
        # Initiate output with current value
        if initialise:
            func(self)

    def output(self, device=None, msg=None):
        logging.info(f'{self} from Device {device.name if device else "(no device)"} '
                     f'triggered by message {msg or "(no message)"}')
        for output in self.outputs:
            output(self, device, msg)
