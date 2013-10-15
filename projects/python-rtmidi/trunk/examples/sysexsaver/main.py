#/usr/bin/env python
# -*- coding: utf-8 -*-
#
# sysexsaver.py
#
"""Save all revceived sysex messages to given directory."""

import argparse
import logging
import os
import sys
import time

from datetime import datetime
from os.path import exists, isdir, join


from rtmidi.midiconstants import *
from rtmidi.midiutil import open_midiport
from .manufacturers import manufacturers


log = logging.getLogger('sysexsaver')


class SysexMessage(object):
    @classmethod
    def fromdata(cls, data):
        self = cls()
        if data[0] != SYSTEM_EXCLUSIVE:
            raise ValuError("Message does not start with 0xF0")
        if data[-1] != END_OF_EXCLUSIVE:
            raise ValuError("Message does not end with 0xF7")
        if len(data) < 5:
            raise ValuError("Message too short")
        if data[1] == 0:
            self._manufacturer = (data[1], data[2], data[3])
            self._device = data[5]
        else:
            self._manufacturer = data[1]
            self._device = data[2]

        self._data = data
        return self

    @property
    def manufacturer(self):
        m = manufacturers.get(self._manufacturer)
        if m:
            return m[1] or m[0]

    @property
    def device(self):
        return "0x%02X" % self._device

    def __repr__(self):
        return "".join(["%02X " % b for b in self._data])

    def as_bytes(self):
        if bytes == str:
            return "".join([chr(b) for b in self._data])
        else:
            return bytes(self._data)


class SysexSaver(object):
    """MIDI input callback hanlder object."""

    def __init__(self, portname, directory, debug=False):
        self.portname = portname
        self.directory = directory
        self.debug = debug

    def __call__(self, event, data=None):
        try:
            message, deltatime = event
            if message[:1] == [SYSTEM_EXCLUSIVE]:
                dt = datetime.now()
                log.debug("[%s: %s] Received sysex msg of %i bytes." % (
                    self.portname, dt.strftime('%x %X'), len(message)))
                sysex = SysexMessage.fromdata(message)

                data = dict(timestamp=dt.strftime('%Y%m%dT%H%M%S'))
                data['manufacturer'] = (sysex.manufacturer or 'unknown'
                    ).lower().replace(' ', '_')
                data['device'] = sysex.device

                outfn = join(self.directory,
                    "%(manufacturer)s-%(device)s-%(timestamp)s.syx" % data)

                if exists(outfn):
                    log.error("Output file already exists, will not overwrite.")
                else:
                    data = sysex.as_bytes()
                    with open(outfn, 'wb') as outfile:
                        outfile.write(data)
                        log.info("Sysex message of %i bytes written to '%s'.",
                            len(data), outfn)
        except:
            if self.debug:
                import traceback
                traceback.print_exc()


def main(args=None):
    """Save revceived sysex message to directory given on command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', '--outdir', default=os.getcwd(),
        help="Output directory (default: current working directory).")
    parser.add_argument('-p',  '--port', dest='port',
        help='MIDI output port number (default: ask)')
    parser.add_argument('-v',  '--verbose', action="store_true",
        help='verbose output')

    args = parser.parse_args(args if args is not None else sys.argv)

    logging.basicConfig(format="%(name)s: %(levelname)s - %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO)

    try:
        midiin, port = open_midiport(args.port)
    except IOError as exc:
        log.error(exc)
        return 1
    except (EOFError, KeyboardInterrupt):
        return 0

    ss = SysexSaver(port, args.outdir, args.verbose)

    log.debug("Attaching MIDI input callback handler.")
    midiin.set_callback(ss)
    log.debug("Enabling reception of sysex messages.")
    midiin.ignore_types(sysex=False)

    log.info("Waiting for sysex reception. Press Control-C to exit.")
    try:
        # just wait for keyboard interrupt in main thread
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('')
    finally:
        log.debug("Exit.")
        midiin.close_port()
        del midiin

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
