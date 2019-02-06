#!/usr/bin/env python3
"""
    pre.di.c. sysEQ generator curves ported from FIRtro.

    Calculates the target curve of the loudspeaker system.
    
    WORK IN PROGRESS
"""

import sys
import numpy as np
import yaml
import basepaths as bp
import getconfigs as gc
import curves

# SYSEQ magnitude curve path (!) work in progress
SYSEQ_MAG_PATH = 'SYSEQ.dat' # R20_ext-target_mag.dat

if __name__ == '__main__':
    
    # Read target parameteres inside loudspeaker definition file
    try:
        lspk_path = sys.argv[1]
        lspk_path += f'/{lspk_path.split("/")[-1]}.yml'
        with open( lspk_path , 'r' ) as f:
            lspk_config = yaml.load( f.read() )
        room_gain    = lspk_config['room_gain']   
        house_corner = lspk_config['house_corner']
        house_atten  = lspk_config['house_atten']
    except:
        print( 'Error reading loudspeaker definition file' )
        sys.exit()

    # Prepare target curve
    freq  = np.loadtxt( f'{bp.config_folder}/{gc.config["frequencies"]}' )
    curve = np.zeros(len(freq))

    #if system_eq   # Former option from FIRtro, but on
    if True:        # pre.di.c target will be always applied
        if house_atten > 0:
            house = curves.HouseCurve( freq, house_corner, house_atten )
        else:
            house = np.zeros( len(freq) )
        room = curves.RoomGain( freq, room_gain )
        curve = curve + house + room

    # Write data to file
    np.savetxt (SYSEQ_MAG_PATH, curve)
    print( f'Curve stored at: {SYSEQ_MAG_PATH}' )
