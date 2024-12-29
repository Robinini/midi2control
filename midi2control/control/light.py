import logging
from leglight import LegLight, discover

"""
Lighting control outputs which can be added as output to a device mapping.

Uses the leglight library for Elgato lights. Other manufacturers could be similarly implemented
"""


def get_elgato_display(display_name):
    """
    Gets light display based on provided name

    :param display_name: (str) Elgato display name
    :return: Leglight instance or None if not found
    """
    for l in discover(2):
        if l.display == display_name:
            return l

class ElgatoLight(LegLight):
    """
    Extended LegLight class with methods that can be used as a callable function for a device mapping.

    The color and brightness steps help to reduce the number of requests sent to the light
    which can be easily overwhelmed when control inputs are frequent

    :param display_name: (str) Elgato display name
    :param address: IP address of light
    :param port: IP port number of light
    :param color_step: (int) Color change steps. If mapping input is below this value, brightness not changed
    """
    def __init__(self, display_name=None, address=None, port=9123, color_step=500, brightness_step=10):
        if display_name:
            light = get_elgato_display(display_name)
            address = light.address
            port = light.port
        LegLight.__init__(self, address=address, port=port)
        self.color_step = color_step
        self.brightness_step = brightness_step

    def switch(self, mapping, device=None, msg=None):
        """
        Toggle light state from on to off or off to on based on mapping state.

        Can be used as a callable function for a device mapping

        :param mapping: midi.mapping MidiMap based object triggering this method
        :param device: midi.device Device associated with this mapping (unused)
        :param msg: mido message received from the device (unused)
        :return: None
        """
        if mapping.current_state:
            self.on()
        else:
            self.off()

    def set_color(self, mapping, device=None, msg=None):
        """
        Change light color based on mapping state.

        Can be used as a callable function for a device mapping

        :param mapping: midi.mapping MidiMap based object triggering this method
        :param device: midi.device Device associated with this mapping (unused)
        :param msg: mido message received from the device (unused)
        :return: None
        """

        # Convert range 0-1 to 2900-7000
        new_color = 2900 + mapping.current_state * (7000 - 2900)
        if not self.color_step or abs(new_color - self.isTemperature) > self.color_step or new_color in (7000, 2900):
            self.color(new_color)
        else:
            logging.debug(f'{self} color change {abs(new_color - self.isTemperature)} '
                          f'below step value {self.color_step}, not changed')

    def set_brightness(self, mapping, device=None, msg=None):
        """
        Change light brightness based on mapping state.

        Can be used as a callable function for a device mapping

        :param mapping: midi.mapping MidiMap based object triggering this method
        :param device: midi.device Device associated with this mapping (unused)
        :param msg: mido message received from the device (unused)
        :return: None
        """

        # brightness 0-100
        new_brightness = 100 * mapping.current_state
        if not self.brightness_step or abs(new_brightness - self.isBrightness) > self.brightness_step or new_brightness in (0, 100):
            self.brightness(new_brightness)
        else:
            logging.debug(f'{self} brightness change {self.isBrightness} > {new_brightness} '
                          f'below step value {self.brightness_step}, not changed')