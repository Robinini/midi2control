# Midi-Controller
 
Use the input of any MIDI device to trigger actions.

For example - a DJ deck can be used to control scrubbing in a video editor, turn lights on 
or be used as a mouse or virtual gamepad.

## Overview

Buttons, keys and sliders of a MIDI device can be configured with mappings. These mappings monitor the current state of the 
input (eg: on/off or position) and trigger functions which may use the current state of the device control.

A number of possible control outputs for the mouse, keyboard and other devices are provided.

## Features
- Support for any MIDI device
  - uses [Mido](https://mido.readthedocs.io/) to connect to MIDI devices and send/receive MIDI messages
  - Controllers for Pioneer devices are currently configured
    - Buttons, rotating dials, sliders, jog-wheels and file browser supported
    - The complete layout of the Pioneer Serato DDJ-SB device is configured
- Multiple triggered outputs can be added to each device control
- Buttons can be set as a toggled or normal with LED Lights providing feedback
- Buttons can be grouped, similar to HTML radio inputs
- Stable disconnect and reconnection of devices
- Switchable modes for different uses (eg: Editing or Gaming) using the file browser control input

## Basic Use

### Requirements

The software requires essentially the [mido](https://mido.readthedocs.io/) python library.

Depending on what outputs are configured, the following may also be required:

- [PyAutoGUI](https://pypi.org/project/PyAutoGUI/)
- [leglight](https://pypi.org/project/leglight/)
- [vgamepad](https://pypi.org/project/vgamepad/)

### Main Concepts

```midi2control.midi.device Device```

Represents the MIDI device and can be extended for specific manufacturers or products.

This listens for MIDI messages and passes relevant messages to the ```MidiMap``` based instances associated with this device.

Different modes can be set up to allow the device to switch assigned mapping profiles for different uses, eg: 'Gaming', 'Editing' etc...

```midi2control.midi.mapping MidiMap```

These mappings are associated with a device profile and handle relevant messages.

They maintain an internal state (eg:True/False/float) which can be accessed by output control.  

They can have multiple control outputs assigned to them, which are each triggered on a relevant MIDI message.

Child classes of the ```MidiMap``` class are provided for specific control inputs like buttons, sliders and browsers. Each behave slightly differently according to their purpose, for example:

- ```midi2control.midi.pioneer Slide``` can be inverted, centered in the middle (eg: for a Tempo +/- slider) or the output limited to step intervals (to reduce the number of output triggers)
- ```midi2control.midi.pioneer JogDial``` can be inverted or limited to a max/min internal rotation state (eg: max. 1 rotation)
- ```midi2control.midi.pioneer Press``` can be toggle switches or simple buttons. They can work independently or as a group

```Output Controls```

Are attached to the ```MidiMap``` instances and are triggered when a relevant MIDI message is received.

They can be any function which should accept (but not necessarily use) the following parameters:
- `mapping`: `midi.mapping MidiMap` based object triggering this method. The `mapping.current_state` may be useful.
- `device`: `midi.device Device` associated with this mapping
- `msg`: [Mido](https://mido.readthedocs.io/) message received from the device

n.b: These functions are called sequentially and are therefore blocking. You may wish to thread/throttle these functions.

A number of output functions/methods are provided for typical use cases. The [advanced Example](../examples/3_complex_device_modes.py) uses them. 

The module `midi2control.control` 
- provides a simple `output` closure function which can be used to create a control output from a function and arguments.
- Gamepad control outputs which can be added as output to a device mapping.
- Keyboard and Mouse outputs are provided using the packages [vgamepad](https://pypi.org/project/vgamepad/) and [pyautogui](https://pyautogui.readthedocs.io/en/latest/) under the hood.

### Preconfigured Controller
 [Example](../examples/1_minimum_example.py) for preconfigured Pioneer Serato DDJ-SB:
```python 
from midi2control.midi.pioneer.ddj_sb import DDJ_SB

# Initiate Pioneer DDJ-SB device
ddj = DDJ_SB()

# Monitor inputs (nb: This will not do anything apart from logging the input)
ddj.monitor_inputs()

# the monitor_inputs method above is blocking. For non-blocking use check_inputs() in a loop
```

The DDJ-SB was configured using the information [here](https://www.pioneerdj.com/-/media/pioneerdj/software-info/controller/ddj-sb/ddj-sb_list_of_midi_messages_e.pdf).

The generic mapping classes in ```midi2control.midi.pioneer``` can be used to configure many pioneer controllers similarly. 


### Manual Configuration
 [Example](../examples/2_simple_midi_mapping_configuration.py) for manual configuration of a generic MIDI device:

```python 

from midi2control.midi.device import Device
from midi2control.midi.mapping import MidiMap
from midi2control.control import output

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
```

The [advanced Example](../examples/3_complex_device_modes.py) explains how different configuration 'modes' can be set up 
and some of the advanced outputs available, for example the virtual gamepad.



