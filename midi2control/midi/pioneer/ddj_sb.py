import time
from threading import Thread
from midi2control.midi.mapping import map_copy
from midi2control.midi.device import Device
from midi2control.midi.pioneer.pioneer import *

# Note on mappings. Each mapping below are set up for both shift on and off position - i.e: ignore the shift state
MODE_SELECTOR = [Browser('BROWSE:ROTATE', channel=6, control=[64, 100]),
           Press('BROWSE:PRESS', channel=6, note=[65, 66])]

BROWSER = [Press('LOAD:Deck1', channel=6, note=[70, 88]),
           Press('LOAD:Deck2', channel=6, note=[71, 89]),
           Press('BACK', channel=6, note=[101, 102])
           ]


MIXER = [Slide('CROSSFADER', channel=6, control=(31, 63), center=True),
         Rotate('FILTER:Deck1', channel=6, control=[(23, 55)]),
         Rotate('FILTER:Deck2', channel=6, control=[(24, 56)]),
         Rotate('HEADPHONES MIX', channel=6, control=[(5, 37)]),
         ]

DECK1 = [Press('PLAY/PAUSE:Deck1', channel=0, note=[11, 71]),
         Press('CUE:Deck1', channel=0, note=[12, 72]),
         Press('SYNC:Deck1', channel=0, note=[88, 92]),
         JogDial('JOG DIAL:Platter:rotate:Deck1', channel=0, control=[34, 35, 31]),
         Press('JOG DIAL:Platter:touch:Deck1', channel=0, note=[54, 53, 103]),
         JogDial('JOG DIAL:Wheel side:Deck1', channel=0, control=[33, 38]),
         Slide('TEMPO:Deck1', channel=0, control=[(0, 32), (5, 37)], center=True),
         Press('VINYL:Deck1', channel=0, note=[23, 78], toggle=True),
         Press('KEYLOCK:Deck1', channel=0, note=[26, 96], toggle=True),
         Press('SHIFT:Deck1', channel=0, note=63, toggle=True),
         # Mixer controls for deck
         Slide('CH FADER:Deck1', channel=0, control=(19, 51)),
         Rotate('EQ HIGH:Deck1', channel=0, control=(7, 39)),
         Rotate('EQ MID:Deck1', channel=0, control=(11, 43)),
         Rotate('EQ LOW:Deck1', channel=0, control=(15, 47)),
         Press('CUE:Headphone:Deck1', channel=0, note=[84, 104], toggle=True),
         #Performance Pads
         Press('HOT CUE mode:Deck1', channel=0, note=[27, 105], radio='Pads1'),
         Press('AUTO LOOP mode:Deck1', channel=0, note=[30, 107], radio='Pads1'),
         Press('MANUAL LOOP mode:Deck1', channel=0, note=[32, 109], radio='Pads1'),
         Press('SAMPLER mode:Deck1', channel=0, note=[34, 111], radio='Pads1', initial_state=True),
         ]

DECK2 = map_copy(DECK1)
for r in DECK2:
    r.name = r.name.replace('Deck1', 'Deck2')
    r.channel = 1
    if r.radio:
        r.radio = r.radio.replace('1', '2')

FX1 = [Press('FX1-1 ON', channel=4, note=[71, 99], toggle=True),
       Press('FX1-2 ON', channel=4, note=[72, 100], toggle=True),
       Press('FX1-3 ON', channel=4, note=[73, 101], toggle=True),
       Rotate('FX1-1', channel=4, control=(2, 34)),
       Rotate('FX1-2', channel=4, control=(4, 36)),
       Rotate('FX1-3', channel=4, control=(6, 38)),
       Rotate('FX1 BEATS', channel=4, control=(0, 32)),
       ]

FX2 = map_copy(FX1)
for r in FX2:
    r.name = r.name.replace('FX1', 'FX2')
    r.channel = 5

PADS1 = [Press('PERFORMANCE PAD 1:Deck1', channel=7, note=[0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120]),
         Press('PERFORMANCE PAD 2:Deck1', channel=7, note=[1, 9, 17, 25, 33, 41, 49, 57, 65, 73, 81, 89, 97, 105, 113, 121]),
         Press('PERFORMANCE PAD 3:Deck1', channel=7, note=[2, 10, 18, 26, 34, 42, 50, 58, 66, 74, 82, 90, 98, 106, 114, 122]),
         Press('PERFORMANCE PAD 4:Deck1', channel=7, note=[3, 11, 19, 27, 35, 43, 51, 59, 67, 75, 83, 91, 99, 107, 115, 123]),
         ]

PADS2 = map_copy(PADS1)
for r in PADS2:
    r.name = r.name.replace('Deck1', 'Deck2')
    r.channel = 8

##################################################################################################################

class DDJ_SB(Device):
    def __init__(self, name='PIONEER DDJ-SB:PIONEER'):
        # NB: Make copy of maps declared above to preserve the originals
        # (otherwise they will also have outputs assigned)
        # We will however use the original MODE_SELECTOR and allow modification and reuse of modes
        Device.__init__(self, name=name, midi_maps={None: MODE_SELECTOR + map_copy(BROWSER) + map_copy(MIXER) +
                                                          map_copy(DECK1) + map_copy(DECK2) + map_copy(FX1)
                                                          + map_copy(FX2) + map_copy(PADS1) + map_copy(PADS2)})
        # Send DJ.App connected signal - ths will prompt current positions to be broadcast
        self.outport.send(mido.Message('note_on', channel=11, note=9))
        self.animate()

    def animate(self):
        """
        Blink keys configured in current mode
        :return:
        """

        def buttons():
            return [m for m in self.midi_maps.get(self.mode).values() if m.__class__ == Press]

        def blink():
            for i in range(5):
                for m in buttons():
                    m.led_on(self)
                time.sleep(0.5)
                for m in buttons():
                    m.led_off(self)
            # Restore according to current status
            for m in buttons():
                if m.current_state:
                    m.led_on(self)

        # Run in thread to allow continued use of device
        Thread(target=blink).start()