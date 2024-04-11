#!/usr/bin/env python
"""Convert joystick axis position into MIDI Control Change value in-/decrements."""

import os
import sys

import pygame
from rtmidi.midiutil import open_midioutput


class Mapping:
    def __init__(self, cc=7, ch=0, inc=1, minval=0, maxval=127):
        self.cc = max(0, min(127, cc))
        self.ch = max(0, min(15, ch))
        self.minval = max(0, min(127, minval))
        self.maxval = max(0, min(127, maxval))
        self.inc = inc
        self.value = 0.0
        self.cc_value = -1

    def update(self, value, threshold):
        if abs(value) >= threshold:
            self.value = max(self.minval, min(self.maxval, self.value + self.inc * value))

            if int(self.value) != int(self.cc_value):
                self.cc_value = self.value
                return True


# Configuration

# How fast the joystick events are polled.
UPDATES_PER_SECOND = 20
# Axis absolute value must exceed this threshold before controler value changes
THRESHOLD = 0.3
# Which axis maps to which control change
CONFIG = {
    # Config for Axis 1
    1: Mapping(cc=11, inc=-0.3),
    # Config for Axis 0
    0: Mapping(cc=12),
    # etc...
    4: Mapping(cc=15, inc=-0.3),
    3: Mapping(cc=14),
}

# We need to init the pygame.display module to use the event queue
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.display.init()
clock = pygame.time.Clock()

# Initialize the first joystick.
pygame.joystick.init()

if pygame.joystick.get_count():
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
else:
    sys.exit("No joysticks found.")


try:
    midiout, name = open_midioutput(sys.argv[1] if len(sys.argv) > 1 else None)
except (EOFError, KeyboardInterrupt):
    sys.exit()
else:
    print("Opened MIDI output {}.".format(name))

# Main Program Loop
try:
    # Loop until the user clicks the close button.
    done = False
    active = []

    while not done:
        # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
        # JOYBUTTONUP, JOYHATMOTION
        for event in pygame.event.get(): # User did something.
            if event.type == pygame.QUIT: # If user clicked close.
                done = True # Flag that we are done so we exit this loop.
            elif event.type == pygame.JOYBUTTONUP:
                print("Joystick button {} released.".format(event.button))
                if event.button == 2:  # 'X' button
                    done = True
                    print("Exit by button press.")
            elif event.type == pygame.JOYAXISMOTION:
                axis = event.axis
                if axis in CONFIG:
                    if abs(event.value) >= THRESHOLD:
                        active.append(axis)
                    elif axis in active:
                        active.remove(axis)

        # we're polling instead of using the event queue,
        # so holding the joystick in one direction keeps updating the value
        for axis in active:
            mapping = CONFIG[axis]
            value = joystick.get_axis(axis)

            #print("Axis {} value: {:>6.3f}".format(axis, value))

            if mapping.update(value, THRESHOLD):
                msg = [0xB0 + mapping.ch, mapping.cc, int(mapping.value) & 0x7F]
                print("SEND: {!r}".format(msg))
                midiout.send_message(msg)


        # Limit poll rate to UPDATES_PER_SECOND.
        clock.tick(UPDATES_PER_SECOND)
except KeyboardInterrupt:
    print("\nInterrupted.")

pygame.quit()
