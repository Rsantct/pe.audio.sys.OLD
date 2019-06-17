#!/usr/bin/env python3

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
    Starts predic audio system

    Usage:
    initaudio.py    core | scripts | all

    core:       jack, brutefir, ecasound, server
    scripts:    everything else (players and clients)
    all:        all of the above
"""

import sys
import os
import time
from subprocess import Popen, check_output, run

import stopaudio
import predic as pd
import basepaths as bp
import getconfigs as gc


if gc.config['load_ecasound']:
    import peq_control

import jack # needed to check for jack ports when trying restoring the input.

def limit_level(level_on_startup, max_level_on_startup):
    """limit volume as specified in config.ini"""

    # if fixed volume on startup
    if level_on_startup:
        level = level_on_startup
    elif max_level_on_startup:
        if gc.state['level'] > max_level_on_startup:
            level = max_level_on_startup
        else:
            level = gc.state['level']
    else:
        level = gc.state['level']
    pd.client_socket('level ' + str(level))

def init_jack():
    """loads jack server"""

    jack_cmd_list = ([gc.config['jack_path']]
                        + gc.config['jack_options'].split()
                        + ['-r'] + [str(gc.speaker['fs'])])
    if 'alsa' in gc.config['jack_options']:
        jack_cmd_list += ['-d' + gc.config['system_card']]
    elif not 'dummy' in gc.config['jack_options']:
        print('\n(startaudio) error starting jack: unknown backend')
        sys.exit(-1)

    # Some systems runs Pulseaudio, pasuspender will release cards and launch jackd
    if 'pulseaudio' in check_output("pgrep -fl pulseaudio", shell=True).decode():
        jack_cmd_list = ['pasuspender', '--'] + jack_cmd_list

    jack = Popen(jack_cmd_list)

    # waiting for jackd:
    if pd.wait4result('jack_lsp', 'system', tmax=10):
        print('\n(startaudio) jack started :-)')
    else:
        print('\n(startaudio) error starting jack')
        sys.exit()

def init_brutefir():
    """loads brutefir"""

    # cd to brutefir config folder so filter paths are relative to this
    # folder in brutefir_config
    os.chdir(bp.loudspeakers_folder + gc.config['loudspeaker'])
    print(f'\n(startaudio) starting brutefir on {os.getcwd()}')
    Popen( f"{gc.config['brutefir_path']} {gc.config['brutefir_options']} \
             brutefir_config".split() )
    # waiting for brutefir
    if  pd.wait4result('echo "quit" | nc localhost 3000', 'Welcome',
        tmax=5, quiet=True):
        print('\n(startaudio) brutefir started :-)')
    else:
        print('\n(startaudio) error starting brutefir')
        sys.exit()

def init_ecasound():
    """loads ecasound"""
    if gc.config['load_ecasound']:
        print('\n(startaudio) starting ecasound')
        ecsFile = (f"{bp.config_folder}PEQx{gc.config['ecasound_filters']}"
                    f"_defeat_{gc.speaker['fs']}.ecs")
        if not os.path.exists(ecsFile):
            print('(startaudio) error: cannot find ' + ecsFile)
            print('             check ecasound_filters in config.yml')
            sys.exit(-1)
        ecsCmd = '-q --server -s:' + ecsFile
        ecasound = Popen([gc.config['ecasound_path']] + ecsCmd.split())
        # waiting for ecasound:
        if  pd.wait4result('jack_lsp', 'ecasound', tmax=5, quiet=True):
            print('(startaudio) ecasound started :-)')
            #notice: ecasound autoconnects to brutefir in ports.
        else:
            print('(startaudio) error starting ecasound')
            sys.exit(-1)


def init_server():
    """loads server"""

    print('\n(startaudio) starting server\n')
    server_path = os.path.expanduser( gc.config['server_path'] )
    try:
        control = Popen( ['python3', server_path, 'control'] )
    except:
        print('\n(startaudio) server didn\'t load')
        sys.exit() # initaudio stopped

    # Waiting for the server
    total_time = rem_time = 10
    while rem_time:
        print(f'(startaudio) waiting for server ({(total_time-rem_time)}s)')
        time.sleep(1)
        try:
            # we must use close() to stop connection
            # and watch till no exception
            pd.client_socket('quit')
            break
        except:
            pass
        rem_time -= 1
    if rem_time:
        print('\n(startaudio) server started :-)')
    else:
        print('\n(startaudio) server not accesible Bye :-/')
        sys.exit() # initaudio stopped

def init_state_settings():
    """restore audio settings as stored in state.yaml
       and takes care of options to reset some of them
    """

    # optional tone reset
    if gc.config['tone_reset_on_startup']:
        pd.client_socket('bass 0')
        pd.client_socket('treble 0')
    else:
        pd.client_socket('bass ' + str(gc.state['bass']))
        pd.client_socket('treble ' + str(gc.state['treble']))

    # optional balance reset
    if gc.config['balance_reset_on_startup']:
        pd.client_socket('balance 0')
    else:
        pd.client_socket('balance ' + str(gc.state['balance']))

    # optional loudness reset
    if gc.config['loudness_reset_on_startup']:
        pd.client_socket('loudness_track off')
        pd.client_socket('loudness_ref 0')
    else:
        pd.client_socket('loudness_track '
            + ('on' if gc.state['loudness_track'] else 'off'))
        pd.client_socket('loudness_ref ' + str(gc.state['loudness_ref']))

    # optional midside reset ( formerly mono reset)
    if gc.config['midside_reset_on_startup']:
        pd.client_socket('midside off')
    else:
        pd.client_socket('midside ' + gc.state['midside'])
    
    # optional solo reset
    if gc.config['solo_reset_on_startup']:
        pd.client_socket('solo off')
    else:
        pd.client_socket('solo ' + gc.state['solo'])

    # optional limited volume on start
    limit_level(gc.config['level_on_startup']
                , gc.config['max_level_on_startup'])

    # restore DRC_set
    pd.client_socket( 'drc ' + str( gc.state['DRC_set'] ) )

    # XO_set will be adjusted when restoring inputs

    # restore PEQ_set
    if gc.config['load_ecasound']:
        peqSet  = gc.state['PEQ_set']
        speaker,_,_ = gc.get_speaker()
        peqFile = speaker['PEQ'][peqSet]
        if peqFile != 'none':
            peq_control.loadPEQini( peqFile )

def init_inputs():
    """restore selected input as stored in state.ini"""

    input = gc.state['input']
    if not input in gc.config['avoid_inputs_on_startup'] and input != 'none':
        print(f'\n(startaudio) restoring input: {input}')
    else:
        return

    # wait for input ports to be up
    ports = pd.gc.inputs[input]['in_ports']
    jc = jack.Client('tmp')
    # lets try 20 times to connect to input ports
    loops = 20
    while loops:
        channels = ('L','R')
        n = len(channels)
        for port_name in ports:
            if jc.get_ports(port_name):
                n -=1
        if n == 0:
            break
        time.sleep(gc.config['command_delay'] * 0.5)
        loops -= 1
    if loops:
        # input ports up and ready :-)
        pd.client_socket('input ' + gc.state['input'], quiet=True)
    else:
        # input ports are down :-(
        print(f'\n(startaudio) time out restoring input \'{input}\''
                                        ', ports not available')

def main(run_levels):

    # Jack, Brutefir, Ecasound, Server
    if 'core' in run_levels or 'all' in run_levels:
        # load basic audio kernel
        init_jack()
        init_brutefir()
        init_ecasound()
        init_server()

    # Scripts for inboard players and others services
    if 'scripts' in run_levels or 'all' in run_levels:
        # launch external scripts, sources and clients
        print('\n(startaudio): starting init scripts...')
        for line in [ x for x in open(bp.init_list_path)
                                # ignore commented out and blank lines
                                if x.strip() and not '#' in x.strip()[0] ]:
            # dispise options if incorrectly set
            script = line.strip().split()[0]
            path = f'{bp.init_scripts_folder}{script}'
            try:
                p = Popen(f'{path} start'.split())
                print(f'pid {p.pid:4}: {script}')
                with open(f'{bp.pids_folder}{script}.pid', 'w') as pidfile:
                    pidfile.write(f'{p.pid}')
            except OSError as err:
                print(f'error launching script:\n\t{err}')
            except:
                print(f'problem launching script {line}')

    # restoring previous state
    init_state_settings()

    # restoring inputs
    init_inputs()

    # some info
    pd.show(state=gc.state)

if __name__ == '__main__':

    # select runlevels
    if sys.argv[1:]:
        run_levels = sys.argv[1:]

    else:
        print(__doc__)
        sys.exit()

    print( '\n(startaudio) stopping proccesses\n' )
    stopaudio.main(run_levels)

    print( '\n(startaudio) starting runlevel ' + " ".join(run_levels) )
    main(run_levels)
