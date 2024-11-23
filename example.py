from midi2control.midi.pioneer.ddj_sb import DDJ_SB
from midi2control.control.mouse import Scroll


import logging
logger = logging.getLogger()
logger.setLevel('DEBUG')


"""
ToDO: Notes

Device:
    Robust connect (while lop with waiting)
    Robust disconnect (routinely check for devices match device name in background) - Raise Error on disconnect

    LED feedback for pioneer. Properly implement 

Mappings:
    Different 'modes' in mappins
    Cleverer MApping config structure
        allow None for chanel etc as wildcard and more complicated multiples.
            NB: Dict can have list tuple as key, perhaps that will help
    Allow multiple siderKnob pairs (eg for when SHIFT on or off)

-------------
Further steps:
-------------
Full config DDJ-SB left and right

Messaging output: 
    Keyboard, Mouse
    Gamepad
    MQTT Bridge (output [publish] and as 'Device' [subscribe] (Tipp: expliot wildcard) etc.

Mode creation function/example

"""

ddj = DDJ_SB()
ddj.monitor_inputs()

#m2g.device.midi_maps.get('Vinyl Right').outputs.append(Scroll())


