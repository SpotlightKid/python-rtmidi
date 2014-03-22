# MIDI Drum sequencer prototype, by Michiel Overtoom, motoom@xs4all.nl
#
# For midi drum notes, see http://en.wikipedia.org/wiki/General_MIDI#Percussion  
# For an OSX software midi synthesizer, see http://notahat.com/simplesynth/

import datetime
import time
import threading
import random   

import rtmidi
import rtmidi.midiutil               
import rtmidi.midiconstants
           
timenow = time.time
timesleep = time.sleep

class Sequencer(threading.Thread):
    def __init__(self, midiout, interval, pattern): 
        super(Sequencer, self).__init__()
        self.midiout = midiout
        self.interval = interval        
        self.pattern = pattern
        self.start()           
        
    def run(self): 
        self.done = False
        self.callcount = 0
        self.started = timenow()
        while not self.done:          
            self.worker()
            self.callcount += 1
            # Compensate for drift: calculate the time when the worker should be called again.
            nexttime = self.started + self.callcount * self.interval
            timetowait = nexttime - timenow() 
            timesleep(timetowait)
        print "Done"
     
    def worker(self):
        """Variable time worker function (i.e., output notes, emtpy queues, etc)""" 
        self.pattern.playstep(self.midiout)



class Drumpattern(object):
    intensities = {
        "-": 0,
        "m": 60,
        "x": 100,
        }      
        
    def __init__(self, pattern):
        self.instruments = []
        for line in pattern:            
            parts = line.strip().split(" ", 2)
            if len(parts) == 3:
                patch, strokes, description = parts
                patch = int(patch)
                self.instruments.append((patch, strokes)) 
                self.steps = len(strokes)
        self.step = 0
                        
    def reset(self):
        self.step = 0
        
    def playstep(self, midiout):
        for ins in self.instruments:
            patch, strokes = ins
            c = strokes[self.step]
            velocity = Drumpattern.intensities[c]
            if velocity:
                note_on = [9|rtmidi.midiconstants.NOTE_ON, patch, velocity]
                midiout.send_message(note_on)
        self.step += 1             
        if self.step >= self.steps:
            self.step = 0
                      

if __name__ == "__main__":

    funkydrummer = """               
           ,...,...,...,...
        42 xxxxx-x-xxxxx-xx Closed Hi-hat
        46 -----x-x-----x-- Open Hi-hat
        38 ----x--m-m-mx--m Snare
        36 x-x-------x--x-- Bassdrum
        """

    p = Drumpattern(funkydrummer.splitlines())
    midiout, port_name = rtmidi.midiutil.open_midiport(0, "output")
    s = Sequencer(midiout, 0.17, p) # TODO: proper BPM calculation.
    timesleep(6) # Let sequencer run for a few seconds.
    s.done = True # And kill it.
    s.join()
    del midiout 
