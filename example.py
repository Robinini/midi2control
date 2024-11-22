from midi2control.midi.pioneer.ddj_sb import DDJ_SB
from midi2control.control.mouse import Scroll


import logging
logger = logging.getLogger()
logger.setLevel('DEBUG')


"""
ToDO: Notes

Allow None for chanel etc as wildcard
Allow multiple siderKnob pairs (eg for when SHIFT on or off)

Messaging output


"""

ddj = DDJ_SB()
ddj.monitor_inputs()

#m2g.device.midi_maps.get('Vinyl Right').outputs.append(Scroll())


