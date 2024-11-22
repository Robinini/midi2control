import logging
import mido
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

    def reset(self):
        logging.debug(f'Resetting {self.name}')
        self.current_state = None

    def message(self, device, msg):
        """

        :param msg: mido midi message
        :param controller: Device controller triggering this message
        :return:
        """
        pass

    def output(self, device, msg):
        logging.info(f'{self.name}, value: {self.current_state} from {device.name} triggred by message {msg}')
        for output in self.outputs:
            output(self, device, msg)
