from midi2control.midi.device import Device
from midi2control.midi.pioneer.pioneer import *
#########################################################################



class DDJ_SB(Device):
    def __init__(self, name='PIONEER DDJ-SB:PIONEER'):
        Device.__init__(self, name=name,
                        midi_maps=[ JogDial('Jogwheel Right', channel=1, control=[34, 35, 31, 33, 38], invert=True),
                                    Slide('Tempo Right', channel=6, control=[31, 63], invert=False, center=True),
                                    Rotate('Filter Right', channel=6, control=[24, 56], invert=False, center=False),
                                    Press('Vinyl Right', channel=1, note=[23, 78], feedback=None),
                                    Toggle('Sampler Right', channel=1, note=[34, 111], feedback=None),])