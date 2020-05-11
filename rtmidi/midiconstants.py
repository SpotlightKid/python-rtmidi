# -*- coding: utf-8 -*-
"""Definitions of midi events, controller numbers and parameters."""

###################################################
# Midi channel events (the most common events)
# Also called "Channel Voice Messages"

NOTE_OFF = 0x80
# 1000cccc 0nnnnnnn 0vvvvvvv (channel, note, velocity)

NOTE_ON = 0x90
# 1001cccc 0nnnnnnn 0vvvvvvv (channel, note, velocity)

POLY_AFTERTOUCH = POLYPHONIC_PRESSURE = POLY_PRESSURE = 0xA0
# 1010cccc 0nnnnnnn 0vvvvvvv (channel, note, velocity)

# see Channel Mode Messages for Controller Numbers
CONTROLLER_CHANGE = CONTROL_CHANGE = 0xB0
# 1011cccc 0ccccccc 0vvvvvvv (channel, controller, value)

PROGRAM_CHANGE = 0xC0
# 1100cccc 0ppppppp (channel, program)

CHANNEL_AFTERTOUCH = CHANNEL_PRESSURE = MONO_PRESSURE = 0xD0
# 1101cccc 0ppppppp (channel, pressure)

PITCH_BEND = 0xE0
# 1110cccc 0vvvvvvv 0wwwwwww (channel, value-lo, value-hi)


###################################################
# Channel Mode Messages (Continuous Controller)
# All CCs have the same status byte (0xBn).
# The controller number is the first data byte

# High resolution continuous controllers (MSB)

BANK_SELECT = BANK_SELECT_MSB = 0x00
MODULATION = MODULATION_WHEEL = MODULATION_WHEEL_MSB = 0x01
BREATH_CONTROLLER = BREATH_CONTROLLER_MSB = 0x02
FOOT_CONTROLLER = FOOT_CONTROLLER_MSB = 0x04
PORTAMENTO_TIME = PORTAMENTO_TIME_MSB = 0x05
DATA_ENTRY = DATA_ENTRY_MSB = 0x06
VOLUME = CHANNEL_VOLUME = CHANNEL_VOLUME_MSB = 0x07
BALANCE = BALANCE_MSB = 0x08
PAN = PAN_MSB = 0x0A
EXPRESSION = EXPRESSION_CONTROLLER = EXPRESSION_CONTROLLER_MSB = 0x0B
EFFECT_CONTROL_1 = EFFECT_CONTROL_1_MSB = 0x0C
EFFECT_CONTROL_2 = EFFECT_CONTROL_2_MSB = 0x0D
GENERAL_PURPOSE_CONTROLLER_1 = GENERAL_PURPOSE_CONTROLLER_1_MSB = 0x10
GENERAL_PURPOSE_CONTROLLER_2 = GENERAL_PURPOSE_CONTROLLER_2_MSB = 0x11
GENERAL_PURPOSE_CONTROLLER_3 = GENERAL_PURPOSE_CONTROLLER_3_MSB = 0x12
GENERAL_PURPOSE_CONTROLLER_4 = GENERAL_PURPOSE_CONTROLLER_4_MSB = 0x13

# High resolution continuous controllers (LSB)

BANK_SELECT_LSB = 0x20
MODULATION_LSB = MODULATION_WHEEL_LSB = 0x21
BREATH_CONTROLLER_LSB = 0x22
FOOT_CONTROLLER_LSB = 0x24
PORTAMENTO_TIME_LSB = 0x25
DATA_ENTRY_LSB = 0x26
VOLUME_LSB = CHANNEL_VOLUME_LSB = 0x27
BALANCE_LSB = 0x28
PAN_LSB = 0x2A
EXPRESSION_LSB = EXPRESSION_CONTROLLER_LSB = 0x2B
EFFECT_CONTROL_1_LSB = 0x2C
EFFECT_CONTROL_2_LSB = 0x2D
GENERAL_PURPOSE_CONTROLLER_1_LSB = 0x30
GENERAL_PURPOSE_CONTROLLER_2_LSB = 0x31
GENERAL_PURPOSE_CONTROLLER_3_LSB = 0x32
GENERAL_PURPOSE_CONTROLLER_4_LSB = 0x33

# Switches

# off: value <= 63, on: value >= 64
SUSTAIN = SUSTAIN_ONOFF = 0x40
PORTAMENTO = PORTAMENTO_ONOFF = 0x41
SOSTENUTO = SOSTENUTO_ONOFF = 0x42
SOFT_PEDAL = SOFT_PEDAL_ONOFF = 0x43
LEGATO = LEGATO_ONOFF = 0x44
HOLD_2 = HOLD_2_ONOFF = 0x45

# Low resolution continuous controllers

# Sound Variation; FX: Exciter On/Off
SOUND_CONTROLLER_1 = 0x46
# Harmonic Content; FX: Compressor On/Off
SOUND_CONTROLLER_2 = 0x47
# Release Time; FX: Distortion On/Off
SOUND_CONTROLLER_3 = 0x48
# Attack Time; FX: EQ On/Off
SOUND_CONTROLLER_4 = 0x49
# Brightness; FX: Expander On/Off
SOUND_CONTROLLER_5 = 0x4A
# Decay Time; FX: Reverb On/Off
SOUND_CONTROLLER_6 = 0x4B
# Vibrato Rate; FX: Delay On/Off
SOUND_CONTROLLER_7 = 0x4C
# Vibrato Depth; FX: Pitch Transpose On/Off
SOUND_CONTROLLER_8 = 0x4D
# Vibrato Delay; FX: Flange/Chorus On/Off
SOUND_CONTROLLER_9 = 0x4E
# Undefined; FX: Special Effects On/Off
SOUND_CONTROLLER_10 = 0x4F
GENERAL_PURPOSE_CONTROLLER_5 = 0x50
GENERAL_PURPOSE_CONTROLLER_6 = 0x51
GENERAL_PURPOSE_CONTROLLER_7 = 0x52
GENERAL_PURPOSE_CONTROLLER_8 = 0x53
# PTC, 0vvvvvvv is the source Note number
PORTAMENTO_CONTROL = PTC = 0x54
HIGH_RESOLUTION_VELOCITY_PREFIX = 0x58
# Reverb Send Level, formerly Ext. Effects Depth
EFFECTS_1 = EFFECTS_1_DEPTH = 0x5B
# formerly Tremelo Depth
EFFECTS_2 = EFFECTS_2_DEPTH = 0x5C
# Chorus Send Level, formerly Chorus Depth
EFFECTS_3 = EFFECTS_3_DEPTH = 0x5D
# formerly Celeste(Detune) Depth
EFFECTS_4 = EFFECTS_4_DEPTH = 0x5E
# formerly Phaser Depth
EFFECTS_5 = EFFECTS_5_DEPTH = 0x5F
# controller value byte should be 0
DATA_INCREMENT = 0x60
# controller value byte should be 0
DATA_DECREMENT = 0x61
NRPN_LSB = NON_REGISTERED_PARAMETER_NUMBER_LSB = 0x62
NRPN_MSB = NON_REGISTERED_PARAMETER_NUMBER_MSB = 0x63
RPN_LSB = REGISTERED_PARAMETER_NUMBER_LSB = 0x64
RPN_MSB = REGISTERED_PARAMETER_NUMBER_MSB = 0x65

# Channel Mode messages

# controller value byte should be 0
ALL_SOUND_OFF = 0x78
# controller value byte should be 0
RESET_ALL_CONTROLLERS = 0x79
# 0 = off, 127 = on
LOCAL_CONTROL = LOCAL_CONTROL_ONOFF = 0x7A
# controller value byte should be 0
ALL_NOTES_OFF = 0x7B
# controller value byte should be 0, also causes ANO
OMNI_MODE_OFF = 0x7C
# controller value byte should be 0, also causes ANO
OMNI_MODE_ON = 0x7D
# Mono Mode on / Poly Off; also causes ANO
# 1011nnnn 01111110 0000vvvv
# vvvv > 0 : Number of channels to use (Omni Off).
# vvvv = 0 : Use all available channels (Omni On)
MONO_MODE_ON = 0x7E
# Poly Mode On / Mono Off
# controller value byte should be 0, also causes ANO
POLY_MODE_ON = 0x7F


###################################################
# System Common Messages, for all channels

# 11110000 0iiiiiii 0ddddddd ... 11110111
SYSTEM_EXCLUSIVE = 0xF0

# MIDI Time Code Quarter Frame
# 11110001
MIDI_TIME_CODE = MTC = 0xF1

# 11110010 0vvvvvvv 0wwwwwww (lo-position, hi-position)
SONG_POSITION_POINTER = 0xF2

# 11110011 0sssssss (songnumber)
SONG_SELECT = 0xF3

# 11110100 (0xF4) is undefined
# 11110101 (0xF5) is undefined

# 11110110
TUNING_REQUEST = TUNE_REQUEST = 0xF6

# 11110111 # End of system exclusive
END_OF_EXCLUSIVE = 0xF7


###################################################
# Midifile meta-events

SEQUENCE_NUMBER = 0x00  # 00 02 ss ss (seq-number)
TEXT = 0x01             # 01 len text...
COPYRIGHT = 0x02        # 02 len text...
SEQUENCE_NAME = 0x03    # 03 len text...
INSTRUMENT_NAME = 0x04  # 04 len text...
LYRIC = 0x05            # 05 len text...
MARKER = 0x06           # 06 len text...
CUEPOINT = 0x07         # 07 len text...
PROGRAM_NAME = 0x08     # 08 len text...
DEVICE_NAME = 0x09      # 09 len text...

MIDI_CH_PREFIX = 0x20   # MIDI channel prefix assignment (deprecated)

MIDI_PORT = 0x21        # 21 01 port, deprecated but still used
END_OF_TRACK = 0x2F     # 2f 00
TEMPO = 0x51            # 51 03 tt tt tt (tempo in µs/quarternote)
SMTP_OFFSET = 0x54      # 54 05 hh mm ss ff xx
TIME_SIGNATURE = 0x58   # 58 04 nn dd cc bb
KEY_SIGNATURE = 0x59    # 59 02 sf mi (sf = number of sharps(+) or flats(-)
                        # mi = major(0) or minor (1))
SPECIFIC = 0x7F         # Sequencer specific event


###################################################
# System Realtime messages
# These should not occur in midi files

TIMING_CLOCK = 0xF8
# 0xF9 is undefined
SONG_START = 0xFA
SONG_CONTINUE = 0xFB
SONG_STOP = 0xFC
# 0xFD is undefined
ACTIVE_SENSING = 0xFE
SYSTEM_RESET = 0xFF


###################################################
# META EVENT, it is used only in midi files.
# In transmitted data it means system reset!!!

# 11111111
META_EVENT = 0xFF
ESCAPE_SEQUENCE = 0xF7


###################################################
# Misc constants

FILE_HEADER = 'MThd'
TRACK_HEADER = 'MTrk'

# Timecode resolution: frames per second
FPS_24 = 0xE8
FPS_25 = 0xE7
FPS_29 = 0xE3
FPS_30 = 0xE2


###################################################
# Helper functions

def is_status(byte):
    """Return True if the given byte is a MIDI status byte, False otherwise."""
    return (byte & 0x80) == 0x80  # 1000 0000
