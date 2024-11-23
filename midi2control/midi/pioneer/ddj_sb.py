from midi2control.midi.device import Device
from midi2control.midi.pioneer.pioneer import *
#########################################################################

midi_maps = [JogDial('Jogwheel Right', channel=1, control=[34, 35, 31, 33, 38], invert=True),
             Browser('Browse Wheel', channel=6, control=[64], invert=False),
             Slide('Tempo Right', channel=1, control=[0,32,5,37], invert=False, center=True),
             Rotate('Filter Right', channel=6, control=[24, 56], invert=False, center=False),
             Press('Vinyl Right', channel=1, note=[23, 78], feedback=None),
             Press('Sampler Right', toggle=True, channel=1, note=[34, 111], feedback=None),

             ]

class DDJ_SB(Device):
    def __init__(self, name='PIONEER DDJ-SB:PIONEER'):
        Device.__init__(self, name=name, midi_maps={None: midi_maps})

    def animate(self):
        pass  # ToDo - idea for rn on light x, turn off light y, sleep etc.. On connect
