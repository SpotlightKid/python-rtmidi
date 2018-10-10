Drum Pattern Sequencer
======================

This example was contributed by Michiel Overtoom [1]_. I just embellished it
a bit and added command line option handling. You can see Michiel's original
script in the repository history.

The script ``drumseq.py`` implements a simple drum pattern sequencer, which
reads patterns from text files in a very simple and easy to edit format, and
plays them back as a MIDI note sequence to a given MIDI output.

Each line starts with the MIDI note number of a drum sound and is followed a
sequence of characters indicating at which step this drum should be triggered.

Different characters map to different velocities and a ``.`` signifies velocity
zero, i.e. the drum note will not be triggered at this step. A dash ``-`` is
a tie, neither a note off nor a new note is sent at this step. Each line must
have the same number of steps. One step is nominally a 1/16 note, but you are
free to define a pattern with twelve steps and increase the BPM by a factor of
4/3 to get a triplet-feel.

Lines starting with a hash (``#``) are ignored and can be used for comments
or temporarily muting a drum sound. The third field of each line, after the
pattern sequence, should name or describe the drum sound to use, but you are
free to put there whatever you want, the field is not used by the sequencer.

You can change the MIDI port, channel, bank and program via command line
options and also specify the BPM at which the pattern is played back.

For a mapping of midi notes to General MIDI drum sounds, see
http://en.wikipedia.org/wiki/General_MIDI#Percussion

For a General MIDI compatible software synthesizer, see:

macOS (OS X)
    SimpleSynth_
Linux
    Qsynth_ (GUI) or fluidsynth_ (command line)
Windows
    Builtin

The patterns whose filenames start with ``example_`` are taken from the article
*The Rhythm Method. Effective Drum Programming* published by the Sound on Sound
magazine [2]_.


.. [1] http://www.michielovertoom.com/
.. [2] http://www.soundonsound.com/sos/feb98/articles/rythm.html

.. _simplesynth: http://notahat.com/simplesynth/
.. _qsynth: http://qsynth.sourceforge.net/
.. _fluidsynth: http://sourceforge.net/apps/trac/fluidsynth/
