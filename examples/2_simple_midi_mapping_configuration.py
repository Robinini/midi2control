"""
Simple example defining mapping and output of generic MIDI device

"""

import logging
from midi2control.midi.device import Device, read_midi_devices
from midi2control.midi.mapping import MidiMap
from midi2control.control import output
from midi2control.control.gui import *


# Set to debug mode to see all midi messages, even if not configured with mapping.
# This can help with reverse engineering of a device
logging.getLogger().setLevel('DEBUG')

# List connected device names which can help if it is not known in advance
print(read_midi_devices())

# Initiate generic device with no preset configuration.
dev = Device('VI61:VI61 VI61')

################################################################################3
# Create a midi mapping of key-press of note C2 (lowest note on this keyboard)
c2_map = MidiMap(name='Note-36 hello world', typ='note_on', channel=0, note=36)

# Create a control output which prints 'hello world'
out = output(print, 'Hello World')

# Add this to the c2_mapping as an output
c2_map.add_output(out)

# Add the completed map and output to the device
dev.add_map(c2_map)

# This can also be chained for example the highest key changes window (ctrl+tab)
dev.add_map(MidiMap(name='Note-96 next window', typ='note_on', channel=0, note=96).add_output(ctrl_tab()))

##############################################################################
# Monitor inputs (nb: This should now print 'hello world' when pressing key C2 or change window/cycle on the highest note)
dev.monitor_inputs()

# the monitor_inputs method above is blocking
