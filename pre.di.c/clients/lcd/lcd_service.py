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
# Will watch for files changed on this folder and subfolders:
WATCHED_DIR =       f'{HOME}/pre.di.c/'
# The files we are going to pay attention to:
STATUS_file     = f'{HOME}/pre.di.c/config/state.yml'
LIBRESPOT_file  = f'{HOME}/pre.di.c/.librespot_events'
SPOTIFY_file    = f'{HOME}/pre.di.c/.librespot_events'
ISTREAMS_file   = f'{HOME}/pre.di.c/.istreams_events'
DVB_file        = f'{HOME}/pre.di.c/.dvb_events'
MPD_file        = f'{HOME}/pre.di.c/.mpd_events'

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

    # Definig the set of widgets (widgets_xxxx becomes global variables)
    define_widgets()

    # Adding the widgets to the main screen
    # pre.di.c status widgets
    for wName, wProps in widgets_state.items():
        cmd = f'widget_add scr_1 { wName } string'
        LCD.send( cmd )
    # metadata players widgets
    for wName, wProps in widgets_meta.items():
        cmd = f'widget_add scr_1 { wName } scroller'
        LCD.send( cmd )

def define_widgets():

    # The screen layout draft:
    #       0        1         2
    #       12345678901234567890
    #
    # 1     Vol: -15.0   Bal: -1
    # 2     B:-1 T:-2  LOUD MONO
    # 3     Input: inputname
    # 4     metadata_title_marquee

    # The widget collection definition (as global variables)
    # Values are defaults, later update_status() will add the current 
    # status info or supress the value in case of booleans.
    
    # If position is set to '0 0' the widget will not be displayed
    
    global widgets_state # defined text type when prepare_main_screen
    widgets_state = {
                'input'             : { 'pos':'1  3',    'val':'input:'   },
                'level'             : { 'pos':'1  1',    'val':'vol:'     },
                'headroom'          : { 'pos':'0  0',    'val':'hrm:'     },
                'balance'           : { 'pos':'14 1',    'val':'bal:'     },
                'mono'              : { 'pos':'12 2',    'val':'MONO'     },
                'muted'             : { 'pos':'1  1',    'val':'MUTED    '},
                'bass'              : { 'pos':'1  2',    'val':'b:'       },
                'treble'            : { 'pos':'6  2',    'val':'t:'       },
                'loudness_ref'      : { 'pos':'0  0',    'val':''         },
                'loudness_track'    : { 'pos':'17 2',    'val':'LOUD'     },
                'XO_set'            : { 'pos':'0  0',    'val':'xo:'      },
                'DRC_set'           : { 'pos':'0  0',    'val':'drc:'     },
                'PEQ_set'           : { 'pos':'0  0',    'val':'peq:'     },
                'syseq'             : { 'pos':'0  0',    'val':''         },
                'polarity'          : { 'pos':'0  0',    'val':'pol'      }
                }

    global widgets_meta # defined scroller type when prepare_main_screen
    widgets_meta = {
                'artist'            : { 'pos':'0  0',    'val':'' },
                'album'             : { 'pos':'0  0',    'val':'' },
                'title'             : { 'pos':'0  0',    'val':'' },
                'bottom_marquee'    : { 'pos':'1  4',    'val':'' },
                }

def update_status():
    """ Reads pre.di.c/config/state.yml then updates the LCD """
    # http://lcdproc.sourceforge.net/docs/lcdproc-0-5-5-user.html

    def show_status(data, priority="info"):
        global LEVEL_OLD
        
        for key, value in data.items():
            pos = widgets_state[key]['pos']
            lab = widgets_state[key]['val']

            # If boolean value, will keep the defalul widget value or will supress it
            if type(value) == bool:
                if not value:
                    lab = ''
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

def update_metadata(metadata, mode='composed_marquee', scr='scr_1'):
    """ Reads pre.di.c metadata dict then updates the LCD """
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

        # pre.di.c state has changed
        if path == STATUS_file:
            #print('updating status')
            update_status()

        # a player events file has changed
        if path in (STATUS_file,
                    MPD_file,
                    SPOTIFY_file,
                    LIBRESPOT_file,
                    DVB_file,
                    ISTREAMS_file):
            sleep(1) # avoids bouncing
            # needs decode() because players gives bytes-like
            update_metadata( players.player_get_meta().decode() , mode='composed_marquee')

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
