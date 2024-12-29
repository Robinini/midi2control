"""
Complex example defining mapping and output of generic MIDI device

"""

import logging
logging.getLogger().setLevel('DEBUG')

from midi2control.midi.pioneer.ddj_sb import DDJ_SB
from midi2control.control.light import ElgatoLight
from midi2control.midi.mapping import MidiMap, map_copy
from midi2control.control import output
from midi2control.control.gui import *
from midi2control.control import gamepad

# Set up device with no outputs
ddj = DDJ_SB()

#######################################################################################
# Add control outputs to predefined mappings

# Mode changer - this allows the user to change the mapping mode by rotating the browser and pressing to select the cue'd mode
browser = ddj.get_map('BROWSE:ROTATE')
browser.add_output(ddj.browse_mode)
ddj.get_map('BROWSE:PRESS').add_output(output(ddj.change_mode, mode_index=browser))

# Light - Elgato LAN light
light_rob = ElgatoLight(address='192.168.1.132')

ddj.get_map('CUE:Headphone:Deck2').add_output(light_rob.switch)
ddj.get_map('FILTER:Deck2').add_output(light_rob.set_brightness)
ddj.get_map('EQ LOW:Deck2').add_output(light_rob.set_color)

# Keypresses
ddj.get_map('FX2-1 ON').add_output(press('F1'), initialise=False).toggle=False
ddj.get_map('FX2-2 ON').add_output(hotkey('ctrl', 'c'), initialise=False).toggle=False

# Scroll
deck2 = ddj.get_map('JOG DIAL:Platter:rotate:Deck2')
deck2.step = 0.1
deck2.add_output(scroll(True))

# Mouse movement
ddj.get_map('CH FADER:Deck1').add_output(move_to_x())
ddj.get_map('CH FADER:Deck2').add_output(move_to_y())
ddj.get_map('PERFORMANCE PAD 1:Deck2').add_output(mouse_downup())

ddj.get_map('JOG DIAL:Platter:rotate:Deck1').add_output(move_x())
ddj.get_map('JOG DIAL:Wheel side:Deck1').add_output(move_y())

#######################################################################################
# Add additional profile

# NB: Make copy of maps, otherwise they will also have outputs assigned to originals
from midi2control.midi.pioneer.ddj_sb import MODE_SELECTOR, BROWSER, MIXER, DECK1, DECK2, FX1, FX2, PADS1, PADS2
ddj.add_maps({'Gaming': MODE_SELECTOR + map_copy(BROWSER) + map_copy(MIXER) + map_copy(DECK1) + map_copy(DECK2) +
                        map_copy(FX1) + map_copy(FX2) + map_copy(PADS1) + map_copy(PADS2)})

# Gamepad
user_1 = gamepad.Gamepad()

ddj.get_map('TEMPO:Deck1', 'Gaming').add_output(gamepad.left_trigger(user_1))
ddj.get_map('TEMPO:Deck2', 'Gaming').add_output(gamepad.right_trigger(user_1))
ddj.get_map('JOG DIAL:Platter:rotate:Deck1', 'Gaming').add_output(gamepad.left_joystick_x(user_1))

ddj.get_map('JOG DIAL:Platter:rotate:Deck2', 'Gaming').add_output(gamepad.right_joystick_x(user_1))
ddj.get_map('JOG DIAL:Platter:rotate:Deck2', 'Gaming').max_state = 1  # Limit the rotation (eg: for steering wheel)
ddj.get_map('JOG DIAL:Platter:rotate:Deck2', 'Gaming').min_state = -1  # Limit the rotation (eg: for steering wheel)
ddj.get_map('JOG DIAL:Wheel side:Deck1', 'Gaming').add_output(gamepad.left_joystick_y(user_1))

ddj.get_map('JOG DIAL:Wheel side:Deck2', 'Gaming').add_output(gamepad.right_joystick_y(user_1))
ddj.get_map('JOG DIAL:Wheel side:Deck2', 'Gaming').max_state = 1
ddj.get_map('JOG DIAL:Wheel side:Deck2', 'Gaming').min_state = -1

ddj.get_map('PLAY/PAUSE:Deck2', 'Gaming').add_output(gamepad.button_press(user_1, gamepad.BUTTONS.A))


# Start
ddj.monitor_inputs()

# the monitor_inputs method above is blocking
