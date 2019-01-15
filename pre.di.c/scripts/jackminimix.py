#!/usr/bin/env python3

""" 
    Runs a jackminimix instance as per configured inside:
    
        pre.di.c/clients/bin/jackminimix_start.sh

    usage:    jackminimix.py   start | stop
"""

import sys
from subprocess import Popen

import basepaths as bp


def start():
    cmd = f'{bp.main_folder}/clients/bin/jackminimix_start.sh'
    Popen( cmd )

def stop():
    Popen( 'pkill -f jackminimix'.split() )
    sys.exit()

if __name__ == '__main__':

    if sys.argv[1:]:
        option = sys.argv[1]
        if option == 'start':
            start()
        elif option == 'stop':
            stop()
        else:
            print(__doc__)
    else:
        print(__doc__)
