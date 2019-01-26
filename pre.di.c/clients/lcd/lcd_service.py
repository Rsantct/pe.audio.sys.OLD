#!/usr/bin/env python3

# Copyright (c) 2018 Rafael Sánchez
# This file is part of pre.di.c
# pre.di.c, a preamp and digital crossover
# Copyright (C) 2018 Roberto Ripio
#
# pre.di.c is based on FIRtro https://github.com/AudioHumLab/FIRtro
# Copyright (c) 2006-2011 Roberto Ripio
# Copyright (c) 2011-2016 Alberto Miguélez
# Copyright (c) 2016-2018 Rafael Sánchez
#
# pre.di.c is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pre.di.c is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pre.di.c.  If not, see <https://www.gnu.org/licenses/>.

"""
    A daemon service that displays pre.di.c info on LCD
"""
# Currently this is based on monitoring file changes under the pre.di.c folder

import os
HOME = os.path.expanduser("~")
import sys
from time import sleep
import yaml

import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import basepaths as bp
import lcd_client
import lcdbig
import players

LEVEL_OLD = None
# Will watch for files changed on this folder and subfolders:
WATCHED_DIR =       f'{HOME}/pre.di.c/'
# The files we will pay attention to:
STATUS_file =       f'{HOME}/pre.di.c/config/state.yml'
LIBRESPOT_file =    f'{HOME}/pre.di.c/.librespot_events'
ISTREAMS_file =     f'{HOME}/pre.di.c/.istreams_events'

# Read LCD settings
f = open( f'{bp.main_folder}/clients/lcd/lcd.yml', 'r' )
tmp = f.read()
f.close()
try:
    LCD_CONFIG = yaml.load(tmp)
except:
    print ( 'YAML error reading lcd.yml' )

def show_temporary_screen( message, timeout=LCD_CONFIG['info_screen_timeout'] ):
    """An additional screen to display temporary information"""

    def split_by_n( seq, n ):
        # a generator to divide a sequence into chunks of n units
        while seq:
            yield seq[:n]
            seq = seq[n:]

    # lcdproc manages 1/8 seconds
    timeout = 8 * timeout

    # Will try to define the screen, if already exist will receive 'huh?'
    ans = LCD.query('screen_add scr_info')
    if not 'huh?' in ans:
        LCD.send(f'screen_set scr_info -cursor no -priority foreground -timeout {str(timeout)}' )
        LCD.send('widget_add scr_info info_tit title')
        LCD.send('widget_add scr_info info_txt2 string')
        LCD.send('widget_add scr_info info_txt3 string')
        LCD.send('widget_add scr_info info_txt4 string')

    # Define the screen title (at line 1)
    LCD.send('widget_set scr_info info_tit "pre.di.c info:"')

    # Display the temporary message
    line = 2
    for data in split_by_n(message, 20):
        LCD.send('widget_set scr_info info_txt' + str(line) + ' 1 ' + str(line) + ' "' + data + '"')
        line += 1
        if line > 4:
            break

def prepare_main_screen():
    """ Defines pre.di.c info main screen 'src_1' and his set of widgets """
    # Adding the screen itself:
    LCD.send('screen_add scr_1')

    # Preparing the set of widgets (widgets becomes a global variable)
    prepare_widgets()

    # Adding the widgets to the screen
    for wName, wProps in widgets.items():
        cmd = f'widget_add scr_1 { wName } string'
        #print(cmd)
        LCD.send( cmd )

def prepare_widgets():

    # The screen layout draft:
    #       0        1         2
    #       12345678901234567890
    #
    # 1     Vol: -15.0   Bal: -1
    # 2     B:-1 T:-2  LOUD MONO
    # 3     Input: inputname
    # 4     DRC:   drcname

    # The widget collection definition (as global variable)
    # Values are defaults, later update_status() will add the current 
    # status info or supress the value in case of booleans.
    global widgets
    widgets = { 'input'             : { 'pos':'1  3',    'val':'input:'   },
                'level'             : { 'pos':'1  1',    'val':'vol:'     },
                'headroom'          : { 'pos':'0  0',    'val':'hrm:'     },
                'balance'           : { 'pos':'14 1',    'val':'bal:'     },
                'mono'              : { 'pos':'17 2',    'val':'MONO'     },
                'muted'             : { 'pos':'1  1',    'val':'MUTED    '},
                'bass'              : { 'pos':'1  2',    'val':'b:'       },
                'treble'            : { 'pos':'6  2',    'val':'t:'       },
                'loudness_ref'      : { 'pos':'0  0',    'val':''         },
                'loudness_track'    : { 'pos':'12 2',    'val':'LOUD'     },
                'XO_set'            : { 'pos':'0  0',    'val':'xo:'      },
                'DRC_set'           : { 'pos':'1  4',    'val':'drc:'     },
                'PEQ_set'           : { 'pos':'0  0',    'val':'peq:'     },
                'syseq'             : { 'pos':'0  0',    'val':''         },
                'polarity'          : { 'pos':'0  0',    'val':'pol'      }
                }

def update_status():
    """ Reads pre.di.c/config/state.yml then updates the LCD """
    # http://lcdproc.sourceforge.net/docs/lcdproc-0-5-5-user.html

    def show_status(data, priority="info"):
        global LEVEL_OLD
        
        for key, value in data.items():
            pos = widgets[key]['pos']
            lab = widgets[key]['val']

            # If boolean value, will keep the defalul widget value or will supress it
            if type(value) == bool:
                if not value:
                    lab = ''
            else:
                lab += str(value)

            # sintax:  widget_set <screen> <widget> <coordinate> "<text>"
            cmd = f'widget_set scr_1 { key } { pos } "{ lab }"'
            #print(cmd)
            LCD.send( cmd )
            
        if LEVEL_OLD != data['level']:
            lcdbig.show_level( str(data['level']) )
            LEVEL_OLD = data['level']

    with open(STATUS_file, 'r') as f:
        show_status( yaml.load( f.read() ) )

class changed_files_handler(FileSystemEventHandler):
    """
        This is a handler that will do something when some file has changed
    """

    def on_modified(self, event):

        path = event.src_path

        # pre.di.c state has changed
        if path == STATUS_file:
            #print('updating status')
            update_status()

        # librespot events file has changed
        if path == LIBRESPOT_file:
            sleep(1)
            meta = players.get_librespot_meta() # this does not works well :-/
            #print('LIBRESPOT:\n', meta)
            pass

        # librespot events file has changed
        if path == ISTREAMS_file:
            sleep(1)
            meta = players.get_mplayer_info('istreams')
            #print('ISTREAMS:\n', meta)
            pass

if __name__ == "__main__":

    # Registers a client under the LCDd server
    LCD = lcd_client.Client('pre.di.c', host='localhost', port=13666)
    if LCD.connect():
        LCD.register()
        print ( '(lcd_service )', f'hello: { LCD.query("hello") }' )
    else:
        print( 'Error registering pre.di.c on LCDd' )
        sys.exit()

    # Prepare the main screen
    prepare_main_screen()
    show_temporary_screen('    Hello :-)')

    # Displays the state of pre.di.c
    update_status()

    # Starts a WATCHDOG to see pre.di.c files changes,
    # and handle these changes to update the LCD display
    #   https://stackoverflow.com/questions/18599339/
    #   python-watchdog-monitoring-file-for-changes
    observer = Observer()
    observer.schedule(event_handler=changed_files_handler(), path=WATCHED_DIR, recursive=True)
    observer.start()
    obsloop = threading.Thread( target = observer.join() )
    obsloop.start()
