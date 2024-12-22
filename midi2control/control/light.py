import logging
from leglight import LegLight, discover


def get_elgato_display(display_name):
    for l in discover(2):
        if l.display == display_name:
            return l

class ElgatoLight(LegLight):
    def __init__(self, display_name=None, address=None, port=9123, color_step=500, brightness_step=10):
        if display_name:
            light = get_elgato_display(display_name)
            address = light.address
            port = light.port
        LegLight.__init__(self, address=address, port=port)
        self.color_step = color_step
        self.brightness_step = brightness_step

    def switch(self, mapping, device=None, msg=None):
        if mapping.current_state:
            self.on()
        else:
            self.off()

    def set_color(self, mapping, device=None, msg=None):
        # Convert range 0-1 to 2900-7000
        new_color = 2900 + mapping.current_state * (7000 - 2900)
        if not self.color_step or abs(new_color - self.isTemperature) > self.color_step or new_color in (7000, 2900):
            self.color(new_color)
        else:
            logging.debug(f'{self} color change {abs(new_color - self.isTemperature)} '
                          f'below step value {self.color_step}, not changed')

    def set_brightness(self, mapping, device=None, msg=None):
        # brightness 0-100
        new_brightness = 100 * mapping.current_state
        if not self.brightness_step or abs(new_brightness - self.isBrightness) > self.brightness_step or new_brightness in (0, 100):
            self.brightness(new_brightness)
        else:
            logging.debug(f'{self} brightness change {self.isBrightness} > {new_brightness} '
                          f'below step value {self.brightness_step}, not changed')