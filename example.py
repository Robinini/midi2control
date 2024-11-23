from midi2control.midi.pioneer.ddj_sb import DDJ_SB
from midi2control.control.mouse import Scroll


import logging
logger = logging.getLogger()
logger.setLevel('DEBUG')


"""
ToDO: Notes

Browser

Different 'modes' in mAppins

Robust conect/dosconnect (routinely check for devices match device name in backgrund

MAppings:
 Cleverer allow None for chanel etc as wildcard and more complicated multiples.
 NB: Dict can have list tuple as keyy, perhaps that will help
Allow multiple siderKnob pairs (eg for when SHIFT on or off)

Messaging output

"""

ddj = DDJ_SB()
ddj.monitor_inputs()

#m2g.device.midi_maps.get('Vinyl Right').outputs.append(Scroll())


