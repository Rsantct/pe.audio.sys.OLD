#!/usr/bin/env python3
"""
    Calculates the target curve of the loudspeaker system.
   
    usage: do_target.py   /path/to/yourLoudspeakerFolder
    
    (i) You need to define yourLoudspeaker.yml file accordingly
"""

import sys
import numpy as np
from scipy.signal import hilbert
import yaml
import basepaths as bp
import getconfigs as gc
import curves

import matplotlib.pyplot as plt

def do_plot():
    # notice freq is already log spaced
    # and mag is in dB
    fig = plt.figure()
    fig.subplots_adjust(hspace=.5)
    ax0 = fig.add_subplot(211)
    ax0.set_ylim(-3, 9)
    ax0.semilogx(freq, eq_mag)
    ax0.set_title("mag (dB)")
    ax1 = fig.add_subplot(212)
    ax1.set_ylim(-.5, .5)
    ax1.semilogx(freq, eq_pha * np.pi / 180)
    ax1.set_title("pha (deg)")
    plt.show()

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
        print(__doc__)
        sys.exit()

    # Filenames
    syseq_mag_path = f'{lspk_path.replace(".yml", "_target_mag.dat")}.candidate'
    syseq_pha_path = f'{lspk_path.replace(".yml", "_target_pha.dat")}.candidate'

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
    # Derive the phase ( notice mag is in dB )
    eq_pha = np.angle( ( hilbert( np.abs( 10**(eq_mag/20) ) ) ) )

    # Write data to file
    np.savetxt (syseq_mag_path, eq_mag)
    np.savetxt (syseq_pha_path, eq_pha)
    print( f'Target curves stored at:\n{syseq_mag_path}\n{syseq_pha_path}' )

    try:
        do_plot()
    except:
        print ( 'cannot pyplot' )
