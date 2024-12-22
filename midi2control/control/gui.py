import pyautogui


# ToDO - improve responsiveness with large movements - scale and needs to be integer?

def vscroll(clicks=1):
    def func(mapping, device=None, msg=None):
        delta = clicks if mapping.current_state > mapping.previous_state else -clicks
        pyautogui.vscroll(delta, _pause=False)
    return func


def hscroll(clicks=1):
    def func(mapping, device=None, msg=None):
        delta = clicks if mapping.current_state > mapping.previous_state else -clicks
        pyautogui.hscroll(delta, _pause=False)
    return func
