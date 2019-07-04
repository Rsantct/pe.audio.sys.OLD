#!/usr/bin/env python3
"""
    Controls jackminimix    
"""
# https://github.com/Rsantct/pre.di.c/blob/master/pre.di.c/doc/80_mixer.md
# Unfortunately direct udp messages via netcat does not work for me, 
# neither I was able to use the pure Python OSC implementation python-osc 
# because not available under Berryconda (Python Anaconda distro for Raspberry Pi)... 
# So here we use oscchief, a nice OSC command line tool.

# (i) You need to have the executable oscchief
#     Visit https://github.com/hypebeast/oscchief to download and compile
#     If you use an armhf machine like a Raspberry Pi we provide the binary here:
#       pe.audio.sys/pre.di.c/doc/armhf_binaries/oscchief

import argparse
from subprocess import run, check_output
import sys

def get_args():

    parser = argparse.ArgumentParser()

    parser.add_argument('--ip', default='localhost',
        help='The ip of the OSC server')

    parser.add_argument('--port', type=int, default=9995,
        help='The port the OSC server is listening on')

    # The first option '--input' is the attribute name when refering to it, 
    # next options will be treated as alias.
    parser.add_argument('--input', '--i', '-i', type=int, default=0,
        help='The mixer channel 1-4')

    parser.add_argument('--gain', '--g', '-g', type=int, default=0,
        help='The channel gain -99...+99 (dB)')

    return parser.parse_args()

def get_port():
    port=9995
    try:
        lines = check_output( 'pgrep -fa jackminimix'.split() ).decode()
        for line in lines.split('\n'):
            if 'minimix -p' in line:
                port = int( line.split('-p')[1].strip().split()[0] )
    except:
        print('jackminimix process not found')
        sys.exit(-1)
    return port
    
if __name__ == '__main__':
    
    args = get_args()
    
    cmd = f'oscchief send { args.ip } { str(get_port()) } \
           /mixer/channel/set_gain ii { args.input } { args.gain }'

    print(cmd)
    run( cmd.split() )

