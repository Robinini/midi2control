from midi2control.midi.pioneer.ddj_sb import DDJ_SB
from midi2control.control.mouse import Scroll


import logging
logger = logging.getLogger()
logger.setLevel('INFO')


"""
ToDO: Future

Device:
    Robust connect (while lop with waiting)
    Robust disconnect (routinely check for devices match device name in background) - Raise Error on disconnect

Radio Group to mimic hardwired group deselect

-------------
Further steps:
-------------

Messaging output: 
    Keyboard, Mouse
    Gamepad
    MQTT Bridge (output [publish] and as 'Device' [subscribe] (Tip: exploit None wildcard) etc.

Mode creation function/example

"""

ddj = DDJ_SB()
import time


ddj.monitor_inputs()

#m2g.device.midi_maps.get('Vinyl Right').outputs.append(Scroll())


