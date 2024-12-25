# Midi-Controller
 
Use the input of any MIDI device to trigger actions.

For example - a DJ deck can be used to control scrubbing in a video editor, turn lights on 
or be used as a mouse or virtual gamepad.

## Overview

Buttons, keys and sliders of a MIDI device can be configured with mappings. These mappings monitor the current state of the 
input (eg: on/off) and trigger functions which may use the current state of the device control.

A number of possible control outputs for the mouse, keyboard and other devices are provided.

## Features
- Support for any MIDI device
  - the library uses [Mido](https://mido.readthedocs.io/) to connect to MIDI devices and send/receive MIDI messages)
  - Controllers for Pioneer controllers are currently configured
    - Buttons, rotating dials, sliders, jog-wheels and file browser supported
    - The complete layout of the Pioneer Serato DDJ-SB is configured
- Multiple triggers can be added to each device control
- Buttons can be set as a toggled or normal with LED Lights providing feedback
- Buttons can be grouped, similar to HTML radio inputs
- Stable disconnect and reconnection of devices
- Switchable modes for different uses (eg: Editing or Gaming) using file browser control

## Basic Use

### Preconfigured
 [Example](../examples/1_minimum_example.py) for preconfigured Pioneer Serato DDJ-SB:
```python 
from midi2control.midi.pioneer.ddj_sb import DDJ_SB

# Initiate Pioneer DDJ-SB device
ddj = DDJ_SB()

# Monitor inputs (nb: This will not do anything apart from logging the input)
ddj.monitor_inputs()

# the monitor_inputs method above is blocking. For non-blocking use check_inputs() in a loop
```

### Manual Configuration

"""
Gamepad control outputs which can be added as output to a device mapping.

Uses gamepad implementations from the vgamepad library

"""