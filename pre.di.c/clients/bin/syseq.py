#!/usr/bin/env python3
"""
    pre.di.c. sysEQ generator curves ported from FIRtro.

    Calculates the target curve of the loudspeaker system.
"""

import sys
import numpy as np
from signal.scipy import hilbert
import yaml
import basepaths as bp
import getconfigs as gc
import curves

if __name__ == '__main__':
    
    # Read target parameteres inside loudspeaker definition file
    try:
        lspk_path   = sys.argv[1]
        lspk_name = f'{lspk_path.split("/")[-1]}'
        lspk_path  += f'/{lspk_name}.yml'
        with open( lspk_path , 'r' ) as f:
            lspk_config = yaml.load( f.read() )
        room_gain    = lspk_config['room_gain']   
        house_corner = lspk_config['house_corner']
        house_atten  = lspk_config['house_atten']
    except:
        print( 'Error reading loudspeaker definition file' )
        sys.exit()

    # Filenames
    syseq_mag_path = f'{lspk_path.replace(".yml", "_target_mag.dat")}.candidate'
    syseq_pha_path = f'{lspk_path.replace(".yml", "_target_mag.dat")}.candidate'

    # Prepare target curve
    freq   = np.loadtxt( f'{bp.config_folder}/{gc.config["frequencies"]}' )
    eq_mag = np.zeros(len(freq))

    if house_atten > 0:
        house = curves.HouseCurve( freq, house_corner, house_atten )
    else:
        house = np.zeros( len(freq) )
    room = curves.RoomGain( freq, room_gain )

    # Compose magnitudes
    eq_mag = eq_mag + house + room
    # Derive the phase
    eq_pha = np.conj( hilbert( np.abs(eq_mag) ) )

    # Write data to file
    np.savetxt (syseq_mag_path, eq_mag)
    np.savetxt (syseq_pha_path, eq_pha)
    print( f'Target curves stored at:\n{syseq_mag_path}\n{syseq_pha_path}' )
