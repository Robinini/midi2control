import pyautogui
import beepy as beep

class Scroll:
    def trigger(self, midi_map=None, controller=None):
        pyautogui.scroll(10)
        for ii in range(1, 7):
            beep.beep(ii)
