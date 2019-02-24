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
import json

import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import basepaths as bp
import lcd_client
#import lcdbig
import players

LEVEL_OLD = None

# 'loudness_track' as global because loudness_monitor value does not
# belong to the pre.di.c status dict and the updater needs to kwow about it.
loudness_track = False
# An auxiliary counter to divide the high refresh rate of LOUDNESSMON_file
lmc = 0

# Will watch for files changed on this folder and subfolders:
WATCHED_DIR      = f'{HOME}/pre.di.c/'
# The files we are going to pay attention to:
STATUS_file      = f'{HOME}/pre.di.c/config/state.yml'
LIBRESPOT_file   = f'{HOME}/pre.di.c/.librespot_events'
SPOTIFY_file     = f'{HOME}/pre.di.c/.librespot_events'
ISTREAMS_file    = f'{HOME}/pre.di.c/.istreams_events'
DVB_file         = f'{HOME}/pre.di.c/.dvb_events'
MPD_file         = f'{HOME}/pre.di.c/.mpd_events'
LOUDNESSMON_file = f'{HOME}/pre.di.c/.loudness_monitor'

# Reading the LCD SETTINGS:
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

def define_widgets():

    # The screen layout draft:
    #       0        1         2
    #       12345678901234567890
    #
    # 1     v:-15.0  bl:-1  MONO
    # 2     b:+1 t:-2 LOUDref 12
    # 3     inputname     mon 12
    # 4     a_metadata_marquee_

    # The widget collection definition (as global variables)
    # Values are defaults, later update_status() will add the current 
    # status info or supress the value in case of booleans.
    
    # If position is set to '0 0' the widget will not be displayed
    
    global widgets_state # defined text type when prepare_main_screen
    widgets_state = {
                'input'             : { 'pos':'1  3',    'val':''         },
                'level'             : { 'pos':'1  1',    'val':'v:'       },
                'headroom'          : { 'pos':'0  0',    'val':'hrm:'     },
                'balance'           : { 'pos':'10 1',    'val':'bl:'      },
                'mono'              : { 'pos':'17 1',    'val':'MONO'     },
                'muted'             : { 'pos':'1  1',    'val':'MUTED    '},
                'bass'              : { 'pos':'1  2',    'val':'b:'       },
                'treble'            : { 'pos':'6  2',    'val':'t:'       },
                'loudness_ref'      : { 'pos':'15 2',    'val':'ref'      },
                'loudness_track'    : { 'pos':'11 2',    'val':'LOUD'     },
                'XO_set'            : { 'pos':'0  0',    'val':'xo:'      },
                'DRC_set'           : { 'pos':'0  0',    'val':'drc:'     },
                'PEQ_set'           : { 'pos':'0  0',    'val':'peq:'     },
                'syseq'             : { 'pos':'0  0',    'val':''         },
                'polarity'          : { 'pos':'0  0',    'val':'pol'      }
                }

    global widgets_aux # info outside pre.di.c status
    widgets_aux = {
                'loudness_monitor'  : { 'pos':'15 3',    'val':'mon'     }
                }
                
    global widgets_meta # defined scroller type when prepare_main_screen
    widgets_meta = {
                'artist'            : { 'pos':'0  0',    'val':'' },
                'album'             : { 'pos':'0  0',    'val':'' },
                'title'             : { 'pos':'0  0',    'val':'' },
                'bottom_marquee'    : { 'pos':'1  4',    'val':'' },
                }

def prepare_main_screen():
    """ Defines pre.di.c info main screen 'src_1' and his set of widgets """
    # Adding the screen itself:
    LCD.send('screen_add scr_1')

    # Definig the set of widgets (widgets_xxxx becomes global variables)
    define_widgets()

    # Adding the previously defined widgets to the main screen:
    
    # 1) pre.di.c status widgets
    for wName, wProps in widgets_state.items():
        cmd = f'widget_add scr_1 { wName } string'
        LCD.send( cmd )
    # 2) Aux widgets
    for wName, wProps in widgets_aux.items():
        cmd = f'widget_add scr_1 { wName } string'
        LCD.send( cmd )
    # 3) metadata players widgets
    for wName, wProps in widgets_meta.items():
        cmd = f'widget_add scr_1 { wName } scroller'
        LCD.send( cmd )

def update_status():
    """ Reads pre.di.c/config/state.yml then updates the LCD """
    # http://lcdproc.sourceforge.net/docs/lcdproc-0-5-5-user.html

    def show_status(data, priority="info"):
        global LEVEL_OLD
        global loudness_track
        
        for key, value in data.items():
            pos = widgets_state[key]['pos'] # pos ~> position
            lab = widgets_state[key]['val'] # lab ~> label

            # When booleans (loudness_track, muted, mono)
            # will leave the defalul widget value or will supress it
            if type(value) == bool:
                if not value:
                    lab = ''
                # Update global to be accesible outside from auxiliary
                if key == 'loudness_track':
                    loudness_track = value
                    
            # Special case: loudness_ref will be rounded to integer
            #               or void if no loudness_track
            elif key == 'loudness_ref':
                if data['loudness_track']:
                    lab += str( int(round(value,0)) ).rjust(3)
                else:
                    lab = ''
                    
            # Any else key:
            else:
                lab += str(value)

                
            # sintax for string widgets:
            #   widget_set screen widget coordinate "text"
            cmd = f'widget_set scr_1 { key } { pos } "{ lab }"'
            #print(cmd)
            LCD.send( cmd )
            
        if LEVEL_OLD != data['level']:
            #lcdbig.show_level( str(data['level']) )
            LEVEL_OLD = data['level']

    with open(STATUS_file, 'r') as f:
        show_status( yaml.load( f.read() ) )
        
def update_loudness_monitor():
    """ Reads the monitored value inside the file .loudness_monitor
        then updates the LCD display.
    """
    
    def show_loudness_monitor(value):
        wdg = 'loudness_monitor'
        pos = widgets_aux[wdg]['pos']
        lab = widgets_aux[wdg]['val']
        
        value = int( round(value,0) )
        if loudness_track:
            lab += str(value).rjust(3)
        else:
            lab = ''
            
        cmd = f'widget_set scr_1 { wdg } { pos } "{ lab }"'
        #print(cmd)
        LCD.send( cmd )
    
    with open(LOUDNESSMON_file, 'r') as f:
        value = f.read().strip()
        try:
            value = round( float(value), 1)
        except:
            value = 0.0
        show_loudness_monitor( value )

def update_metadata(metadata, mode='composed_marquee', scr='scr_1'):
    """ Reads pre.di.c metadata dict then updates the LCD display """
    # http://lcdproc.sourceforge.net/docs/lcdproc-0-5-5-user.html

    def compose_marquee(md):
        """ compose a string to be displayed on a LCD bottom line marquee.
        """
        
        tmp = '{ "bottom_marquee":"'
        for k,v in json.loads(md).items():
            if k in ('artist', 'album', 'title') and v != '-':
                tmp += k[:2] + ':' + str(v) + ' '
        tmp += '" }'
        
        return tmp
    
    # This compose a unique marquee widget with all metadata fields:
    if mode == 'composed_marquee':
        metadata = json.loads( compose_marquee(metadata) )
    # This is if you want to use separate widgets kind of:
    else:
        metadata = json.loads(metadata)

    for key, value in metadata.items():

        if key in widgets_meta.keys():
        
            pos =       widgets_meta[key]['pos']
            label =     widgets_meta[key]['val']
            label +=    str(value)
        
            left, top   = pos.split()
            right       = 20
            bottom      = top
            direction   = 'm' # (h)orizontal (v)ertical or (m)arquee
            speed       = str( LCD_CONFIG['scroller_speed'] )
            # adding a space for marquee mode
            if direction == 'm':
                label += ' '
        
            # sintax for scroller widgets:
            #   widget_set screen widget left top right bottom direction speed "text"
            cmd = f'widget_set {scr} {key} {left} {top} {right} {bottom} {direction} {speed} "{label}"'
            #print(cmd)
            LCD.send( cmd )

class changed_files_handler(FileSystemEventHandler):
    """
        This is a handler that will do something when some file has changed
    """

    def on_modified(self, event):

        path = event.src_path

        # The pre.di.c state has changed
        if STATUS_file in path:
            update_status()

        # A player event file has changed
        if path in (MPD_file,
                    SPOTIFY_file,
                    LIBRESPOT_file,
                    DVB_file,
                    ISTREAMS_file):
            sleep(1) # avoids bouncing
            # needs decode() because players gives bytes-like
            update_metadata( players.player_get_meta().decode() , mode='composed_marquee')

        # The loudness monitor file has changed
        # loudness monitor changes counter
        global lmc
        if path in (LOUDNESSMON_file):
            lmc += 1        # the auxiliary loudness monitor refresh counter
            if lmc > 10:    # waits for 10 because file update period is 100 ms
                update_loudness_monitor()
                lmc = 0

if __name__ == "__main__":

    # Registers a client under the LCDd server
    LCD = lcd_client.Client('pre.di.c', host='localhost', port=13666)
    if LCD.connect():
        LCD.register()
        print( '(lcd_service )', f'hello: { LCD.query("hello") }' )
    else:
        print( 'Error registering pre.di.c on LCDd' )
        sys.exit()

    # Prepare the main screen
    prepare_main_screen()
    show_temporary_screen('    Hello :-)')

    # Displays the state of pre.di.c
    update_status()
    # Displays update_loudness_monitor
    update_loudness_monitor()
    
    # Displays metadata
    #md =  '{"artist":"Some ARTIST",'
    #md += ' "album":"Some ALBUM",'
    #md += ' "title":"ファイヴ・スポット・アフター・ダーク"}'
    # needs to decode because players gives bytes-like
    update_metadata( players.player_get_meta().decode() , mode='composed_marquee')

    # Starts a WATCHDOG to see pre.di.c files changes,
    # and handle these changes to update the LCD display
    #   https://stackoverflow.com/questions/18599339/
    #   python-watchdog-monitoring-file-for-changes
    observer = Observer()
    observer.schedule(event_handler=changed_files_handler(), path=WATCHED_DIR, recursive=True)
    observer.start()
    obsloop = threading.Thread( target = observer.join() )
    obsloop.start()
