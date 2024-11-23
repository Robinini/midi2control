import logging


class MidiMap:
    def __init__(self, name, typ, channel, control=None, note=None, outputs=None, description=None):
        """
        Mapping. NB This could be tched to multiple devices attached in parallel
        :param name:
        :param type:
        :param channel:
        :param control:
        :param outputs: List of output classes which should have a method trigger() accepting this object and triggering device object
        :param description:
        """
        self.name = name  # unique for device
        self.description = description

        self.type = typ
        self.channel = channel
        self.control = control
        self.note = note

        self.current_state = None

        self.outputs = outputs or list()

        logging.debug(f'Creating mapping {self.name} {f"({self.description})" if self.description else str()}')

    def __str__(self):
        return f"{self.__class__.__name__}, {self.name}, {self.current_state}"

    def reset(self, state=None):
        logging.debug(f'Resetting {self}')
        self.current_state = state
        logging.debug(f'Reset {self}')

    def message(self, device, msg):
        """

        :param msg: mido midi message
        :param controller: Device controller triggering this message
        :return:
        """
        raise NotImplementedError

    def output(self, device, msg):
        logging.info(f'{self} from {device.name} triggered by message {msg}')
        for output in self.outputs:
            output(self, device, msg)
