import logging
import vgamepad as vg

"""
Gamepad control outputs which can be added as output to a device mapping.

Uses gamepad implementations from the vgamepad library

"""


class Gamepad(vg.VX360Gamepad):
    def __init__(self):
        """
        Gamepad class to create gamepad instance using the XBOX-360 model.
        """
        super().__init__()
        logging.debug('Virtual Gamepad created')


class BUTTONS:
    """
    Possible buttons as class variables. Can be used in button_press function, eg:

        <device>.add_output(gamepad.button_press(Gamepad(), BUTTONS.LEFT_SHOULDER))

    """
    DPAD_UP = 0x0001
    DPAD_DOWN = 0x0002
    DPAD_LEFT = 0x0004
    DPAD_RIGHT = 0x0008
    START = 0x0010
    BACK = 0x0020
    LEFT_THUMB = 0x0040
    RIGHT_THUMB = 0x0080
    LEFT_SHOULDER = 0x0100
    RIGHT_SHOULDER = 0x0200
    GUIDE = 0x0400
    A = 0x1000
    B = 0x2000
    X = 0x4000
    Y = 0x8000


def button_press(gamepad, button):
    """
    Creates callable function to execute a gamepad button press

    :param gamepad: the gamepad to use for the press
    :param button: The button to press
    :return: mapping output function suitable to pass to device mapping
    """

    def fun(*args, **kwargs):
        m = args[0]

        if m.current_state:
            logging.debug(f'Pressing button with code {button}')
            gamepad.press_button(button)
        else:
            logging.debug(f'Releasing button with code {button}')
            gamepad.release_button(button)
        gamepad.update()

    return fun


def left_joystick_x(gamepad, invert=False):
    """
    Creates callable function to execute a gamepad left joystick x-axes position change
    :param gamepad: the gamepad to use for the press
    :param invert: if True, the control axis is reversed
    :return: mapping output function suitable to pass to device mapping
    """

    def fun(*args, **kwargs):
        m = args[0]
        state = m.current_state if not invert else -m.current_state
        logging.debug(f'Moving x axes of left joystick to {state}')
        gamepad.left_joystick(x_value=round(state*32767), y_value=gamepad.report.sThumbLY)
        gamepad.update()

    return fun


def left_joystick_y(gamepad, invert=False):
    """
    Creates callable function to execute a gamepad left joystick y-axes position change
    :param gamepad: the gamepad to use for the press
    :param invert: if True, the control axis is reversed
    :return: mapping output function suitable to pass to device mapping
    """

    def fun(*args, **kwargs):
        m = args[0]
        state = m.current_state if not invert else -m.current_state
        logging.debug(f'Moving y axes of left joystick to {state}')
        gamepad.left_joystick(x_value=gamepad.report.sThumbLX, y_value=round(state*32767))
        gamepad.update()

    return fun


def right_joystick_x(gamepad, invert=False):
    """
    Creates callable function to execute a gamepad rigth joystick x-axes position change
    :param gamepad: the gamepad to use for the press
    :param invert: if True, the control axis is reversed
    :return: mapping output function suitable to pass to device mapping
    """

    def fun(*args, **kwargs):
        m = args[0]
        state = m.current_state if not invert else -m.current_state
        logging.debug(f'Moving x axes of right joystick to {state}')
        gamepad.right_joystick(x_value=round(state*32767), y_value=gamepad.report.sThumbLY)
        gamepad.update()

    return fun


def right_joystick_y(gamepad, invert=False):
    """
    Creates callable function to execute a gamepad right joystick y-axes position change
    :param gamepad: the gamepad to use for the press
    :param invert: if True, the control axis is reversed
    :return: mapping output function suitable to pass to device mapping
    """

    def fun(*args, **kwargs):
        m = args[0]
        state = m.current_state if not invert else -m.current_state
        logging.debug(f'Moving y axes of right joystick to {state}')
        gamepad.right_joystick(x_value=gamepad.report.sThumbLX, y_value=round(state*32767))
        gamepad.update()

    return fun


def left_trigger(gamepad, invert=False):
    """
    Creates callable function to execute a gamepad left trigger position change
    :param gamepad: the gamepad to use for the press
    :param invert: if True, the control axis is reversed
    :return: mapping output function suitable to pass to device mapping
    """

    def fun(*args, **kwargs):
        m = args[0]
        # Handle button
        if isinstance(m.current_state, bool):
            state = int(m.current_state) if not invert else -int(m.current_state)
        else:
            state = m.current_state if not invert else -m.current_state
        logging.debug(f'Moving left trigger to {state}')
        gamepad.left_trigger_float(state)
        gamepad.update()

    return fun


def right_trigger(gamepad, invert=False):
    """
    Creates callable function to execute a gamepad right trigger position change
    :param gamepad: the gamepad to use for the press
    :param invert: if True, the control axis is reversed
    :return: mapping output function suitable to pass to device mapping
    """

    def fun(*args, **kwargs):
        m = args[0]
        # Handle button
        if isinstance(m.current_state, bool):
            state = int(m.current_state) if not invert else -int(m.current_state)
        else:
            state = m.current_state if not invert else -m.current_state
        logging.debug(f'Moving right trigger to {state}')
        gamepad.right_trigger_float(value_float=state)
        gamepad.update()

    return fun

