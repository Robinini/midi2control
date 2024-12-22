from midi2control.midi.pioneer.ddj_sb import DDJ_SB


import logging
logger = logging.getLogger()
logger.setLevel('INFO')

ddj = DDJ_SB()

ddj.monitor_inputs()



