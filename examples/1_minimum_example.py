"""
Minimum example using predefined mappings of Pioneer DJ-Decks

"""

import logging
logger = logging.getLogger()
logger.setLevel('INFO')

from midi2control.midi.pioneer.ddj_sb import DDJ_SB

# Initiate Pioneer DDJ-SB device from the predefined configuration
ddj = DDJ_SB()

# Monitor inputs (nb: This will not do anything apart from logging the input)
ddj.monitor_inputs()

# the monitor_inputs method above is blocking. For non-blocking use check_inputs() in a loop


