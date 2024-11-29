from midi2control.midi.pioneer.ddj_sb import DDJ_SB
from midi2control.control.mouse import Scroll


import logging
logger = logging.getLogger()
logger.setLevel('INFO')


"""
ToDO: Future

Device:
    Robust connect (while loop with waiting)
    Robust disconnect (routinely check for devices match device name in background) - Raise Error on disconnect

Mode creation function/example
-------------
Further steps:
-------------

Messaging output: 
    Keyboard, Mouse
    Gamepad
    Sound
    MQTT Bridge (output [publish] and as 'Device' [subscribe] (Tip: exploit None wildcard) etc.



"""

ddj = DDJ_SB()
import time


ddj.monitor_inputs()

#m2g.device.midi_maps.get('Vinyl Right').outputs.append(Scroll())


