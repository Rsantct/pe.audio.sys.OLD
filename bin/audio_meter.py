#!/usr/bin/env python3

""" metering from an audio device
"""

# Thanks to https://python-sounddevice.readthedocs.io

import argparse
import numpy as np
import sounddevice as sd
import queue

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def parse_cmdline():

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-l', '--list-devices', action='store_true',
                        help='list audio devices and exit')

    parser.add_argument('-b', '--block-duration', type=float,
                        metavar='DURATION', default=50,
                        help='block size (default %(default)s milliseconds)')

    parser.add_argument('-d', '--device', type=int_or_str,
                        help='input device (numeric ID or substring)')

    parser.add_argument('-p', '--print', action="store_true", default=False,
                        help='rough level meter print out for testing purposes')

    parser.add_argument('-w', '--writefile', action="store_true", default=False,
                        help='write dB level to "audio_meter" file, only for testing purposes')

    args = parser.parse_args()

    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)

    return args

def print_bars(audiodata):
    """ A funny rough level meter w/o curses ...
        Please wide enough your terminal
    """
    channels = audiodata.shape[1]
    # Range below 0 dBFS to display
    RANGE = 50
    line = ''
    for ch in range( channels ):
        dBs = 20*np.log( np.max( abs( audiodata[:,ch] ) ) )
        # The bar itself
        bar = int(dBs) + RANGE
        # The blank bar chunk
        blanks = RANGE - bar
        line += f' {"*"*bar}{" "*blanks}'
        blanks = RANGE
    print(line, end='\r')
    line = ''

def callback(indata, frames, time, status):
    """ Handler when InputStream has captured audio chunks """
    # If any incident is reported back
    if status:
        print( f'----- {status} -----' )
    # Filling the FIFO
    q.put(indata)

if __name__ == '__main__':

    args = parse_cmdline()

    # FIFO
    q = queue.Queue()

    samplerate = sd.query_devices(args.device, 'input')['default_samplerate']
    channels   = sd.query_devices(args.device, 'input')['max_input_channels']


    with sd.InputStream(device=args.device, callback=callback,
                        blocksize  = int(samplerate * args.block_duration / 1000),
                        samplerate = samplerate,
                        channels   = channels,
                        dither_off = True):

        while True:

            # Reading from the FIFO (a numpy array for both channels)
            audiodata = q.get()
            
            # prints out a rough level bar (only for testing purposes)
            if args.print:
                print_bars( audiodata )

            # Here we find the max sample looking at all audiodata channels
            dBs = 20 * np.log( np.max( abs(audiodata) ) )

            # writes a file (TESTING WORK IN PROGRESS)
            if args.writefile:
                with open('audio_meter', 'w') as f:
                    f.write( str( round(dBs,2) ) )
