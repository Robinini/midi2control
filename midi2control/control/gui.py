import logging
import pyautogui

"""
Mouse and keyboard control outputs which can be added as output to a device mapping

Closures to provide pyautogui functionality.

Furter infomation, see https://pyautogui.readthedocs.io
"""


def click():
    """
    Creates callable function for single mouse click on button down (mapping.current_state evaluates to True).
    Does nothing on button up

    :return: mapping output function suitable to pass to device mapping
    """
    def func(mapping, device=None, msg=None):
        if mapping.current_state:
            logging.debug('Performing single mouse click')
            pyautogui.click()
    return func


def mouse_downup():
    """
    Creates callable function for mouse click on button down (mapping.current_state evaluates to True).
    Releases on button up

    :return: mapping output function suitable to pass to device mapping
    """
    def func(mapping, device=None, msg=None):
        if mapping.current_state:
            logging.debug('Performing mouse click-down')
            pyautogui.mouseDown()
        else:
            logging.debug('Performing mouse click-up')
            pyautogui.mouseUp()
    return func


def double_click():
    """
    Creates callable function for mouse double-click on button down (mapping.current_state evaluates to True).
    Releases on button up

    :return: mapping output function suitable to pass to device mapping
    """
    def func(mapping, device=None, msg=None):
        if mapping.current_state:
            logging.debug('Performing double mouse click')
            pyautogui.doubleClick()
    return func


def scroll(invert=False, scale=800):
    """
    Creates callable function to scroll of the mouse scroll wheel.

    Whether this is a vertical or horizontal scroll depends on the underlying
    operating system.

    :param invert: if True, the control axis is reversed
    :param scale: How the change in mapping state is scaled to determine a scroll pixel value
    :return: mapping output function suitable to pass to device mapping
    """

    def func(mapping, device=None, msg=None):
        if not invert:
            delta = scale * (mapping.current_state - mapping.previous_state)
        else:
            delta = scale * (mapping.previous_state - mapping.current_state)

        # Needs to be at least 1.0 or -1.0 to have an effect
        delta = max(1, delta) if delta > 0 else min(1, delta)

        logging.debug(f'Scrolling {delta} pixels')
        pyautogui.scroll(delta, _pause=False)
    return func


def hscroll(invert=False, scale=800):
    """
    Creates callable function to perform an explicitly horizontal scroll of the mouse scroll wheel,
    if this is supported by the operating system.

    :param invert: if True, the control axis is reversed
    :param scale: How the change in mapping state is scaled to determine a scroll pixel value
    :return: mapping output function suitable to pass to device mapping
    """
    def func(mapping, device=None, msg=None):
        if not invert:
            delta = scale * (mapping.current_state - mapping.previous_state)
        else:
            delta = scale * (mapping.previous_state - mapping.current_state)

        # Needs to be at least 1.0 or -1.0 to have an effect
        delta = max(1, delta) if delta > 0 else min(1, delta)

        logging.debug(f'Horizontal-scrolling {delta} pixels')
        pyautogui.hscroll(delta, _pause=False)

    return func


def move_x(invert=False, scale=800):
    """
    Creates callable function to move the mouse cursor to a point on the screen in the x-axes, relative to its current
    position.

    :param invert: if True, the control axis is reversed
    :param scale: How the change in mapping state is scaled to determine a scroll pixel value
    :return: mapping output function suitable to pass to device mapping
    """
    def func(mapping, device=None, msg=None):
        if not invert:
            delta = scale * (mapping.current_state - mapping.previous_state)
        else:
            delta = scale * (mapping.previous_state - mapping.current_state)

        # Needs to be at least 1.0 or -1.0 to have an effect
        delta = max(1, delta) if delta > 0 else min(1, delta)

        logging.debug(f'Moving mouse {delta} pixels horizontally')
        pyautogui.move(delta, 0, _pause=False)
    return func


def move_y(invert=False, scale=800):
    """
    Creates callable function to move the mouse cursor to a point on the screen in the y-axes, relative to its current
    position.

    :param invert: if True, the control axis is reversed
    :param scale: How the change in mapping state is scaled to determine a scroll pixel value
    :return: mapping output function suitable to pass to device mapping
    """
    def func(mapping, device=None, msg=None):
        if not invert:
            delta = scale * (mapping.current_state - mapping.previous_state)
        else:
            delta = scale * (mapping.previous_state - mapping.current_state)

        # Needs to be at least 1.0 or -1.0 to have an effect
        delta = max(1, delta) if delta > 0 else min(1, delta)

        logging.debug(f'Moving mouse {delta} pixels vertically')
        pyautogui.move(0, delta, _pause=False)

    return func


def move_to_x():
    """
    Creates callable function to move the mouse cursor on the x-axes to a point on the screen relative to the screen width.
    The mapping state should be between 0 (left) and 1.0 (right).

    :return: mapping output function suitable to pass to device mapping
    """
    def func(mapping, device=None, msg=None):
        w, h = pyautogui.size()
        x, y = mapping.current_state * w, None
        if 0 < x <= h:
            logging.debug(f'Moving mouse to horizontal pixel position {x}')
            pyautogui.moveTo(x, y, _pause=False)

    return func


def move_to_y():
    """
    Creates callable function to move the mouse cursor on the y-axes to a point on the screen relative to the screen height.
    The mapping state should be between 0 (top) and 1.0 (bottom).

    :return: mapping output function suitable to pass to device mapping
    """

    def func(mapping, device=None, msg=None):
        w, h = pyautogui.size()
        x, y = None, mapping.current_state * h
        if 0 < y <= h:
            logging.debug(f'Moving mouse to vertical pixel position {y}')
            pyautogui.moveTo(x, y, _pause=False)
        pyautogui.moveTo(None, mapping.current_state * h, _pause=False)

    return func



"""
The following are the valid strings to pass to the press(), key_downup(), and hotkey() functions:
[from https://pyautogui.readthedocs.io/en/latest/keyboard.html]

    ['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(',
    ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
    '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
    'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
    'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
    'browserback', 'browserfavorites', 'browserforward', 'browserhome',
    'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
    'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
    'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
    'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
    'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
    'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
    'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
    'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
    'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
    'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
    'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
    'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
    'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
    'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen',
    'command', 'option', 'optionleft', 'optionright']

"""

def key_downup(key):
    """
    Creates callable function to perform a keyboard key press on button down (mapping.current_state evaluates to True)
    without the release.
    Releases on button up.

    :param key: (str) The key to be pressed down/released
    :return: mapping output function suitable to pass to device mapping
    """
    def func(mapping, device=None, msg=None):
        if mapping.current_state:
            logging.debug(f'Performing {key} keydown')
            pyautogui.keyDown(key)
        else:
            logging.debug(f'Performing {key} keyup')
            pyautogui.keyUp(key)
    return func


def press(key):
    """
    Creates callable function to perform a keyboard key press down, followed by a release.

    :param key: (str) The key to be pressed down/released
    :return: mapping output function suitable to pass to device mapping
    """
    def func(mapping, device=None, msg=None):
        if mapping.current_state:
            logging.debug(f'Performing {key} press')
            pyautogui.press(key)
    return func


def hotkey(*args):
    """
    Creates callable function to perform key down presses on the arguments passed in order, then performs
    key releases in reverse order.

    :param args: The series of keys to press, in order. This can also be a list of key strings to press.
    :return: mapping output function suitable to pass to device mapping
    """
    def func(mapping, device=None, msg=None):
        if mapping.current_state:
            logging.debug(f'Performing {args} hotkey move')
            pyautogui.hotkey(*args)
    return func


def cut():
    """
    Creates callable function to execute a hotkey combination for a cut operation
    :return: mapping output function suitable to pass to device mapping
    """
    return hotkey('ctrl', 'x')


def copy():
    """
    Creates callable function to execute a hotkey combination for a copy operation
    :return: mapping output function suitable to pass to device mapping
    """
    return hotkey('ctrl', 'c')


def paste():
    """
    Creates callable function to execute a hotkey combination for a paste operation
    :return: mapping output function suitable to pass to device mapping
    """
    return hotkey('ctrl', 'v')
