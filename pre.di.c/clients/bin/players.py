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

""" A module that controls and retrieve metadata info from the current player.
    This module is ussually called from a listening server.
"""

# TODO: a command line interface could be useful

import subprocess as sp
import yaml
import mpd
import time
import json

import basepaths as bp

# MPD settings:
MPD_HOST    = 'localhost'
MPD_PORT    = 6600
MPD_PASSWD  = None

# The METADATA GENERIC TEMPLATE for pre.di.c clients, for example the web control page:
# Remember to use copies of this ;-)
METATEMPLATE = {
    'player':   '-',
    'time_pos': '-:-',
    'time_tot': '-:-',
    'bitrate':  '-',
    'artist':   '-',
    'album':    '-',
    'title':    '-'
    }

# Check for the SPOTIFY Client in use:
SPOTIFY_CLIENT = None
librespot_bitrate = '-'
spotify_bitrate   = '-'
# Check if a desktop client is running:
try:
    sp.check_output( 'pgrep -f Spotify'.split() )
    # still pending how to retrieve the Desktop client bitrate
    SPOTIFY_CLIENT = 'desktop'
except:
    pass
# Check if 'librespot' (a Spotify Connect daemon) is running:
try:
    sp.check_output( 'pgrep -f librespot'.split() )
    # Gets librespot bitrate from librespot running process:
    try:
        tmp = sp.check_output( 'pgrep -fa /usr/bin/librespot'.split() ).decode()
        # /usr/bin/librespot --name rpi3clac --bitrate 320 --backend alsa --device jack --disable-audio-cache --initial-volume=99
        librespot_bitrate = tmp.split('--bitrate')[1].split()[0].strip()
    except:
        pass
    SPOTIFY_CLIENT = 'librespot'
except:
    pass

# MPD control, status and metadata
def mpd_client(query):
    """ comuticates to MPD music player daemon """

    def get_meta():
        """ gets info from mpd """

        md = METATEMPLATE.copy()
        md['player'] = 'MPD'

        if mpd_online:

            # We try because not all tracks have complete metadata fields:
            try:    md['artist']   = client.currentsong()['artist']
            except: pass
            try:    md['album']    = client.currentsong()['album']
            except: pass
            try:    md['title']    = client.currentsong()['title']
            except: pass
            try:    md['bitrate']  = client.status()['bitrate']   # given in kbps
            except: pass
            try:    md['time_pos'] = timeFmt( float( client.status()['elapsed'] ) )
            except: pass
            try:    md['time_tot'] = timeFmt( float( client.currentsong()['time'] ) )
            except: pass

            client.close()
        
        return json.dumps( md )

    def state():
        if mpd_online:
            return client.status()['state']

    def stop():
        if mpd_online:
            client.stop()
            return client.status()['state']

    def pause():
        if mpd_online:
            client.pause()
            return client.status()['state']

    def play():
        if mpd_online:
            client.play()
            return client.status()['state']

    def next():
        if mpd_online:
            try:    client.next()   # avoid error when some playlist have wrong items
            except: pass
            return client.status()['state']

    def previous():
        if mpd_online:
            try:    client.previous()
            except: pass
            return client.status()['state']

    def rew():                    # for REW and FF will move 30 seconds
        if mpd_online:
            client.seekcur('-30')
            return client.status()['state']

    def ff():
        if mpd_online:
            client.seekcur('+30')
            return client.status()['state']

    client = mpd.MPDClient()
    try:
        client.connect(MPD_HOST, MPD_PORT)
        if MPD_PASSWD:
            client.password(MPD_PASSWD)
        mpd_online = True
    except:
        mpd_online = False

    result = {  'get_meta':   get_meta,
                'state':      state,
                'stop':       stop,
                'pause':      pause,
                'play':       play,
                'next':       next,
                'previous':   previous,
                'rew':        rew,
                'ff':         ff
             }[query]()

    return result

# Mplayer control
def mplayer_cmd(cmd, service):
    """ Sends a command to Mplayer trough by its input fifo """
    # Notice: Mplayer sends its responses to the terminal where Mplayer was launched,
    #         or to a redirected file.

    # 'seek xxx 0' -> seeks relative xxx seconds (http://www.mplayerhq.hu/DOCS/tech/slave.txt)
    # 'seek xxx 1' -> seeks to xxx %
    # 'seek xxx 2' -> seeks to absolute xxx seconds
    
    if service == 'istreams':
        # useful when playing a mp3 stream e.g. some long playing time podcast url
        if cmd == 'previous':   cmd = 'seek -300 0'
        if cmd == 'rew':        cmd = 'seek -60  0'
        if cmd == 'ff':         cmd = 'seek +60  0'
        if cmd == 'next':       cmd = 'seek +300 0'

    if service == 'dvb':
        # (i) all this stuff is testing and not much useful
        if cmd == 'previous':   cmd = 'tv_step_channel previous'
        if cmd == 'rew':        cmd = 'seek_chapter -1 0'
        if cmd == 'ff':         cmd = 'seek_chapter +1 0'
        if cmd == 'next':       cmd = 'tv_step_channel next'

    sp.Popen( f'echo "{cmd}" > {bp.main_folder}/{service}_fifo', shell=True)

# Mplayer metadata
def get_mplayer_info(service):
    """ gets metadata from Mplayer as per
        http://www.mplayerhq.hu/DOCS/tech/slave.txt """

    md = METATEMPLATE.copy()
    md['player'] = 'Mplayer'

    # This is the file were Mplayer standard output has been redirected to,
    # so we can read there any answer when required to Mplayer slave daemon:
    mplayer_redirection_path = f'{bp.main_folder}/.{service}_events'

    # Communicates to Mplayer trough by its input fifo to get the current media filename and bitrate:
    mplayer_cmd(cmd='get_audio_bitrate', service=service)
    mplayer_cmd(cmd='get_file_name',     service=service)
    mplayer_cmd(cmd='get_time_pos',      service=service)
    mplayer_cmd(cmd='get_time_length',   service=service)

    # Waiting Mplayer ANS_xxxx to be writen to output file
    time.sleep(.25)

    # Trying to read the ANS_xxxx from the Mplayer output file
    with open(mplayer_redirection_path, 'r') as file:
        try:
            tmp = file.read().split('\n')[-5:] # get last 4 lines plus the empty one when splitting
        except:
            tmp = []

    #print('DEBUG\n', tmp)

    # Flushing the Mplayer output file to avoid continue growing:
    with open(mplayer_redirection_path, 'w') as file:
        file.write('')

    # Reading the intended metadata chunks
    if len(tmp) >= 4: # to avoid indexes issues while no relevant metadata are available

        if 'ANS_AUDIO_BITRATE=' in tmp[0]:
            bitrate = tmp[0].split('ANS_AUDIO_BITRATE=')[1].split('\n')[0].replace("'","")
            md['bitrate'] = bitrate.split()[0]

        if 'ANS_FILENAME=' in tmp[1]:
            # this way will return the whole url:
            #md['title'] = tmp[1].split('ANS_FILENAME=')[1]
            # this way will return just the filename:
            md['title'] = tmp[1].split('ANS_FILENAME=')[1].split('?')[0].replace("'","")

        if 'ANS_TIME_POSITION=' in tmp[2]:
            time_pos = tmp[2].split('ANS_TIME_POSITION=')[1].split('\n')[0]
            md['time_pos'] = timeFmt( float( time_pos ) )

        if 'ANS_LENGTH=' in tmp[3]:
            time_tot = tmp[3].split('ANS_LENGTH=')[1].split('\n')[0]
            md['time_tot'] = timeFmt( float( time_tot ) )

    return json.dumps( md )

# Spotify Desktop metadata
def get_spotify_meta():
    """ Gets the metadata info retrieved by the daemon init/spotify_monitor
        which monitorizes a Spotify Desktop Client
    """
    md = METATEMPLATE.copy()
    md['player'] = 'Spotify'
    md['bitrate'] = spotify_bitrate

    try:
        events_file = f'{bp.main_folder}/.spotify_events'
        f = open( events_file, 'r' )
        tmp = f.read()
        f.close()

        tmp = json.loads( tmp )
        # Example:
        # {
        # "mpris:trackid": "spotify:track:5UmNPIwZitB26cYXQiEzdP", 
        # "mpris:length": 376386000, 
        # "mpris:artUrl": "https://open.spotify.com/image/798d9b9cf2b63624c8c6cc191a3db75dd82dbcb9", 
        # "xesam:album": "Doble Vivo (+ Solo Que la Una/Con Cordes del Mon)", 
        # "xesam:albumArtist": ["Kiko Veneno"], 
        # "xesam:artist": ["Kiko Veneno"], 
        # "xesam:autoRating": 0.1, 
        # "xesam:discNumber": 1, 
        # "xesam:title": "Ser\u00e9 Mec\u00e1nico por Ti - En Directo", 
        # "xesam:trackNumber": 3, 
        # "xesam:url": "https://open.spotify.com/track/5UmNPIwZitB26cYXQiEzdP"
        # }

        for k in ('artist', 'album', 'title'):
            value = tmp[ f'xesam:{k}']
            if type(value) == list:
                md[k] = ' '.join(value)
            elif type(value) == str:
                md[k] = value
        
        md['time_tot'] = timeFmt( tmp["mpris:length"]/1e6 )

    except:
        pass

    return json.dumps( md )

# Spotify Desktop control
def spotify_control(cmd):
    """ Controls the Spotify Desktop player
        It is assumed that you have the mpris2-dbus utility 'playerctl' installed.
            https://wiki.archlinux.org/index.php/spotify#MPRIS
        dbus-send command can also work
            http://www.skybert.net/linux/spotify-on-the-linux-command-line/
    """
    # playerctl - Available Commands:
    #   play                    Command the player to play
    #   pause                   Command the player to pause
    #   play-pause              Command the player to toggle between play/pause
    #   stop                    Command the player to stop
    #   next                    Command the player to skip to the next track
    #   previous                Command the player to skip to the previous track
    #   position [OFFSET][+/-]  Command the player to go to the position or seek forward/backward OFFSET in seconds
    #   volume [LEVEL][+/-]     Print or set the volume to LEVEL from 0.0 to 1.0
    #   status                  Get the play status of the player
    #   metadata [KEY]          Print metadata information for the current track. Print only value of KEY if passed
    
    # (!) Unfortunately, 'position' does not work, so we cannot rewind neither fast forward
    if cmd in ('play', 'pause', 'next', 'previous' ):
        sp.Popen( f'playerctl --player=spotify {cmd}'.split() )

    # Retrieving the playback state
    result = ''
    if cmd == 'state':
        try:
            result = sp.check_output( f'playerctl --player=spotify status'.split() ).decode()
        except:
            pass
    # playerctl just returns 'Playing' or 'Paused'
    if 'play' in result.lower():
        return 'play'
    else:
        return 'pause'

# librespot (Spotify Connect client) metatata
def get_librespot_meta():
    """ gets metadata info from librespot """
    # Unfortunately librespot only prints out the title metadata, nor artist neither album.
    # More info can be retrieved from the spotify web, but it is necessary to register
    # for getting a privative and unique http request token for authentication.

    md = METATEMPLATE.copy()
    md['player'] = 'Spotify'
    md['bitrate'] = librespot_bitrate

    try:
        # Returns the current track title played by librespot.
        # 'scripts/librespot.py' handles the libresport print outs to be 
        #                        redirected to 'tmp/.librespotEvents'
        tmp = sp.check_output( f'tail -n1 {bp.main_folder}/.librespot_events'.split() )
        md['title'] = tmp.decode().split('"')[-2]
        # JSON for JavaScript on control web page, NOTICE json requires double quotes:
    except:
        pass

    return json.dumps( md )

# Generic function to get meta from any player: MPD, Mplayer or Spotify
def get_meta():
    """ Makes a dictionary-like string with the current track metadata
        '{player: xxxx, artist: xxxx, album:xxxx, title:xxxx, etc... }'
        Then will return a bytes-like object from the referred string.
    """
    metadata = METATEMPLATE.copy()
    source = predic_source()

    if   'librespot' in source or 'spotify' in source.lower():
        if SPOTIFY_CLIENT == 'desktop':
            metadata = get_spotify_meta()
        elif SPOTIFY_CLIENT == 'librespot':
            metadata = get_librespot_meta()
        
    elif source == 'mpd':
        metadata = mpd_client('get_meta')

    elif source == 'istreams':
        metadata = get_mplayer_info(service=source)

    elif source == 'tdt' or 'dvb' in source:
        metadata = get_mplayer_info(service='dvb')

    else:
        metadata = json.dumps( metadata )

    # As this is used by a server, we will return a bytes-like object:
    return metadata.encode()

# Generic function to control any player
def control(action):
    """ controls the playback """

    source = predic_source()

    if   source == 'mpd':
        result = mpd_client(action)

    elif source.lower() == 'spotify' and SPOTIFY_CLIENT == 'desktop':
        # We can control only Spotify Desktop (not librespot)
        result = spotify_control(action)

    elif 'tdt' in source or 'dvb' in source:
        result = mplayer_cmd(cmd=action, service='dvb')

    elif predic_source() in ['istreams', 'iradio']:
        result = mplayer_cmd(cmd=action, service='istreams')
    
    # Currently only MPD and Spotify Desktop provide 'state' info.
    # 'result' can be 'play', 'pause', stop' or ''.
    if not result:
        result = '' # to avoid None.encode() error

    # As this is used by a server, we will return a bytes-like object:
    return result.encode()

# Gets the current input source on pre.di.c
def predic_source():
    """ retrieves the current input source """
    source = None
    # It is possible to fail while state file is updating :-/
    times = 4
    while times:
        try:
            source = get_predic_state()['input']
            break
        except:
            times -= 1
        time.sleep(.25)
    return source

# Gets the dictionary of pre.di.c status
def get_predic_state():
    """ returns the YAML pre.di.c's status info """

    f = open( bp.main_folder + 'config/state.yml', 'r')
    tmp = f.read()
    f.close()
    return yaml.load(tmp)

# Auxiliary function to format hh:mm:ss
def timeFmt(x):
    # x must be float
    h = int( x / 3600 )         # hours
    x = int( round(x % 3600) )  # updating x to reamining seconds
    m = int( x / 60 )           # minutes from the new x
    s = int( round(x % 60) )    # and seconds
    return f'{h:0>2}:{m:0>2}:{s:0>2}'

# Interface entry function to this module
def do(task):
    """
        This do() is the entry interface function from a listening server.
        Only certain received 'tasks' will be validated and processed,
        then returns back some useful info to the asking client.
    """

    # First clearing the new line
    task = task.replace('\n','')

    # Tasks querying the current music player.
    if   task == 'player_get_meta':
        return get_meta()

    # Playback control. (i) Some commands need to be adequated later, depending on the player,
    # e.g. Mplayer does not understand 'previous', 'next' ...
    elif task[7:] in ('state', 'stop', 'pause', 'play', 'next', 'previous', 'rew', 'ff'):
        return control( task[7:] )

    # A pseudo task, an url to be played back:
    elif task[:7] == 'http://':
        sp.run( f'{bp.main_folder}/init/istreams url {task}'.split() )
