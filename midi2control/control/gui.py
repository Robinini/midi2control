import pyautogui


def vscroll(clicks=1):
    def func(map, device=None, msg=None):
        delta = clicks if map.current_state > map.previous_state else -1*clicks
        pyautogui.vscroll(delta, _pause=False)
    return func


def hscroll(clicks=1):
    def func(map, device=None, msg=None):
        delta = clicks if map.current_state > map.previous_state else -1*clicks
        pyautogui.hscroll(delta, _pause=False)
    return func
