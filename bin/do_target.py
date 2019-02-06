#!/usr/bin/env python3
"""
  Calculates the target curve of the loudspeaker system.

  usage: do_target.py /path/to/yourLoudspeakerFolder [-r] [-c] [-h]

        -rXX    romm_gain    +XX dB
        -cXX    house_corner  XX Hz
        -hXX    house_curve  -XX dB

  (i) You need to define yourLoudspeaker.yml file accordingly
"""

import sys
import numpy as np
from scipy.signal import hilbert
import matplotlib.pyplot as plt
import yaml
import basepaths as bp
import getconfigs as gc
import curves

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
    
    room_gain    = 0
    house_corner = 0 
    house_atten  = 0
    
    # Read options from command line
    for opc in sys.argv[1:]:
        if opc[:2] == '-r':
            room_gain    = float( opc[2:] )
        if opc[:2] == '-c':
            house_corner = float( opc[2:] )
        if opc[:2] == '-h':
            house_atten  = float( opc[2:] )
    
    # Read target parameteres inside loudspeaker definition file
    # (i) Command line takes precedence
    try:
        lspk_path   = sys.argv[1]
        lspk_name = f'{lspk_path.split("/")[-1]}'
        lspk_path  += f'/{lspk_name}.yml'
        with open( lspk_path , 'r' ) as f:
            lspk_config = yaml.load( f.read() )
        if not room_gain:
            room_gain    = lspk_config['room_gain']   
        if not house_corner:
            house_corner = lspk_config['house_corner']
        if not house_atten:
            house_atten  = lspk_config['house_atten']
    except:
        print( 'Error reading loudspeaker definition file' )
        print(__doc__)
        sys.exit()

    # Filenames can be suffixed with the room and house dBs :-)
    suffix = '+' + str(round(room_gain, 1)) + '-' + str(round(house_atten, 1))
    syseq_mag_path = f'{lspk_path.replace(".yml", "_target_mag.dat").replace(".dat", "_"+suffix+".dat")}'
    syseq_pha_path = f'{lspk_path.replace(".yml", "_target_pha.dat").replace(".dat", "_"+suffix+".dat")}'

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
    #eq_pha = np.angle( ( hilbert( np.abs( 10**(eq_mag/20) ) ) ) )
    eq_pha = np.zeros(len(freq))

    # Write data to file
    np.savetxt (syseq_mag_path, eq_mag)
    np.savetxt (syseq_pha_path, eq_pha)
    print( f'Target curves stored at:\n{syseq_mag_path}\n{syseq_pha_path}' )

    try:
        do_plot()
    except:
        print ( 'cannot pyplot' )
