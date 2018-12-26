#!/usr/bin/env python3
"""
    Starts a server listening for some auxiliary tasks as
    - amplifier switch on/off
    - uer macros execution
    
    use:   scripts/aux.py    start | stop
"""

import sys
from subprocess import Popen

def start():
    Popen( ['server_misc.py', 'aux'] ) # if this fails check your paths

def stop():
    Popen( ['pkill', '-KILL', '-f',  'server_misc.py aux'] )
    # harakiri
    Popen( ['pkill', '-KILL', '-f',  'scripts/aux.py'] )

if sys.argv[1:]:
    try:
        option = {
            'start' : start,
            'stop'  : stop
            }[ sys.argv[1] ]()
    except:
        print('(server_aux) bad option')
else:
    print(__doc__)