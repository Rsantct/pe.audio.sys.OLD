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
    Stops predic audio system

    Usage:
    stopaudio.py    core | scripts | all

    core:       jack, brutefir, ecasound, server
    scripts:    everything else (players and clients)
    all:        all of the above
"""

import sys
import os
from subprocess import Popen, run

import basepaths as bp
import getconfigs as gc
import predic as pd

fnull = open(os.devnull, 'w')


def main(run_levels):

    if 'core' in run_levels or 'all' in run_levels:

        # controlserver
        print('(stopaudio) stopping server')
        server_cmdline = os.path.expanduser( gc.config['server_path'] ) + 'control'
        try:
            pd.client_socket('shutdown')
            pd.wait4result(f'pgrep -f "{server_cmdline}"', '', 5, quiet=True)
        except:
            print('(stopaudio) forcing to stop server.py')
            run ( [ 'pkill', '-9', '-f', f'{server_cmdline}' ] , stdout=fnull, stderr=fnull )

        # ecasound
        if gc.config['load_ecasound']:
            print('(stopaudio) stopping ecasound')
            run (['killall', '-KILL', 'ecasound'], stdout=fnull, stderr=fnull )

        # brutefir
        print('(stopaudio) stopping brutefir')
        run ( ['killall', '-KILL', gc.config['brutefir_path'] ], stdout=fnull, stderr=fnull )

        # jack
        print('(stopaudio) stopping jackd')
        run ( 'killall -KILL jackd'.split(), stdout=fnull, stderr=fnull )

    if 'scripts' in run_levels or 'all' in run_levels:

        # stop external scripts, sources and clients
        for line in [ x for x in open(bp.init_list_path)
                              if not '#' in x.strip()[0] ]: # ignore comments
            # dispise options if incorrectly set
            script = line.strip().split()[0]
            script_path = f'{bp.init_scripts_folder}{script}'
            print( "(stopaudio) stopping: " + script_path.replace(bp.main_folder, '') )
            try:
                command = f'{script_path} stop'
                Popen( command.split() )
                pd.kill_pid( script )
                pd.wait4result('pgrep -f ' + script, '', 5, quiet=True)
            except OSError as err:
                print(f'error launching script:\n\t{err}')
            except:
                print(f'problem launching script {line}:\n\t{err}')


if __name__ == '__main__':

    # select runlevels
    if sys.argv[1:]:
        run_levels = sys.argv[1:]

    else:
        print(__doc__)
        sys.exit()

    print('\n(stopaudio) stopping proccesses\n')
    main(run_levels)
