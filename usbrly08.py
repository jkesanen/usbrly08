#!/usr/bin/env python
# -*- coding: utf-8 -*

# Copyright (c) 2018 Jani Kesänen <jani.kesanen+usbrly08@gmail.com>
# All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#
#   * Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

"""A python tool/library for controlling USB-RLY08-B 8 relay output board.

Should also work on following models (control commands are the same):
 
    * USBRLY02
    * USBRLY08
    * USBRLY16
    * USBRLY16L

Tested with python versions 2.7.14 and 3.6.4."""

from __future__ import print_function
import struct

__author__ = "Jani Kesänen"
__copyright__ = "Copyright 2018, Jani Kesänen"
__license__ = "BSD-3"
__version__ = "0.1"

class usbrly():

    # Definitions command bytes
    CMDS = {
        "GET_SERIAL": 56,
        "GET_SW_VERSION": 90,
    
        "GET_STATES": 91,
        "SET_STATES": 92,

        "ALL_ON": 100,
        "FIRST_ON": 101,

        "ALL_OFF": 110,
        "FIRST_OFF": 111
    }

    def __init__(self, fd):
        self.fd = fd


    def set_state(self, relay, state):
        """Set the state of a single relay.

        Args:
            relay: which relay to set (0-7)
            state: (true, false)
        """
        if relay < 0 or relay > 7:
            raise ValueError("Given relay value %d is out of range" % (relay))

        if state:
            controlByte = self.CMDS["FIRST_ON"] + relay
        else:
            controlByte = self.CMDS["FIRST_OFF"] + relay

        self.fd.write([controlByte])


    def set_states(self, states):
        """Set the states of all relays according to given byte.

        Args:
            states: uint8 sized value for relay states.
                0x01 = turns on 1st relay
                0x08 = turns on 4th relay
                0x0A = turns on 2nd and 4th relays
                0xF1 = turns on 1st and 8th relays
        """
        if type(states) != int:
            raise ValueError("states must be given as an int")

        if states < 0 or states > 0xFF:
            raise ValueError("states must be a in range of [0, 255]")

        self.fd.write([self.CMDS["SET_STATES"], states])


    def get_states(self):
        """Get states of all relays.

        Returns:
            An int value representing the relay states [0, 255]
        """
        self.fd.write([self.CMDS["GET_STATES"]])
        states = self.fd.read(1)

        if len(states) != 1:
            raise OSError("get_states failed to read the requested number of bytes")

        return struct.unpack('B', states)[0]
    

    def set_all(self, state):
        """Sets all status to True or False

        Args:
            state: a boolean value to set the relays into
        """
        if state:
            controlByte = self.CMDS["ALL_ON"]
        else:
            controlByte = self.CMDS["ALL_OFF"]

        self.fd.write([controlByte]) 


    def get_serial(self):
        """Get the serial number of the board

        Returns:
            A string of 8 bytes containing the board's serial number
        """
        self.fd.write([self.CMDS["GET_SERIAL"]])
        serial = self.fd.read(8)

        if len(serial) != 8:
            raise OSError("get_serial failed to read the requested number of bytes")

        return serial.decode('ascii')


    def get_sw_version(self):
        """Get the software version of the board.

        Returns:
            A tuple of two bytes: module id and software version.
        """
        self.fd.write([self.CMDS["GET_SW_VERSION"]])
        version = self.fd.read(2)

        if len(version) != 2:
            raise OSError("get_sw_version failed to read the requested number of bytes")

        return struct.unpack("BB", version)


def main():
    import argparse
    import sys

    try:
        import serial
    except ImportError as err:
        print("Importing pyserial failed: {0}".format(err))
        sys.exit(1)

    # Setup tool's command line arguments
    ap = argparse.ArgumentParser(description="USB-RLY controlling tool version %s" % (__version__))

    ap.add_argument('-p', '--port', help='Serial port of the USB-RLY device', required=True)
    ap.add_argument('-t', '--timeout', metavar='SECONDS',
                    type=int, help='Timeout for serial communications')

    controlGroup = ap.add_argument_group('control')
    controlGroup.add_argument('-a', '--all-relays',
                              help='Set all relays to specified state', choices=['on', 'off'])
    controlGroup.add_argument('-n', '--relay-on', help='Set a relay to ON state',
                              type=int, choices=range(0, 8), action='append')
    controlGroup.add_argument('-f', '--relay-off', help='Set a relay to OFF state',
                              type=int, choices=range(0, 8), action='append')

    queryGroup = ap.add_argument_group('query')
    queryGroup.add_argument('-g', '--relays', help='Get the state of the relays', action='store_true')
    queryGroup.add_argument('-s', '--get-serial',
                            help='Get serial number of the board', action='store_true')
    queryGroup.add_argument('-i', '--get-version',
                            help='Get SW version of the board', action='store_true')

    # Parse the given arguments and output an error and exit if invalid arguments were given
    args = ap.parse_args()

    # Open the requested serial port
    s = serial.Serial(args.port, timeout=args.timeout)
    r = usbrly(s)

    # Handle -a / --all-relays
    if args.all_relays == "on":
        r.set_all(True)
    elif args.all_relays == "off":
        r.set_all(False)

    # Handle -n / --relay-on
    if args.relay_on:
        for relay in args.relay_on:
            r.set_state(relay, True)

    # Handle -f / --relay-off
    if args.relay_off:
        for relay in args.relay_off:
            r.set_state(relay, False)

    # Handle -g / --relays
    if args.relays:
        states = r.get_states()
        print("0x%.2x" % (states))
        for i in range(0, 8):
            print("%u %s" % (i, 'on' if states & 1 << i else 'off'))

    # Handle -s / --get-serial
    if args.get_serial:
        print(r.get_serial())

    # Handle -i / --get-version
    if args.get_version:
        version = r.get_sw_version()
        print("%.2x %.2x" % (version[0], version[1]))

    s.close()


if __name__ == "__main__":
    main()
