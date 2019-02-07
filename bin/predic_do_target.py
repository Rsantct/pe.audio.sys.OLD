#!/usr/bin/env python3
"""
  Calculates target curves for a loudspeaker system,
  and shows graphs of them.

  Usage:
  
    predic_do_target.py /path/to/yourLspkFolder [-rXX] [-cXX] [-hXX]

        -rXX    romm_gain    +XX dB
        -cXX    house_corner  XX Hz
        -hXX    house_curve  -XX dB

  (i) If any option is omitted, you need to define them 
      inside 'yourLoudspeaker.yml' file accordingly.
"""

import sys
import numpy as np
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
    
    room_gain    = -1
    house_corner = -1 
    house_atten  = -1
    
    # Read target parameteres from command line
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
        lspk_folder = sys.argv[1]
        if lspk_folder.endswith('/'):   # remove trailing /
            lspk_folder = lspk_folder[:-1]
        lspk_name = f'{lspk_folder.split("/")[-1]}'
        lspk_def  = f'{lspk_folder}/{lspk_name}.yml'

        with open( lspk_def , 'r' ) as f:
            lspk_config = yaml.load( f.read() )

        # precedence if command line
        if room_gain     == -1:
            room_gain    = lspk_config['room_gain']   
        if house_corner  == -1:
            house_corner = lspk_config['house_corner']
        if house_atten   == -1:
            house_atten  = lspk_config['house_atten']

    except:
        print(__doc__)
        print( '    Error reading loudspeaker definition file\n' )
        sys.exit()

    # Filenames suffixed with the room and house dBs :-)
    suffix = '+' + str(round(room_gain, 1)) + '-' + str(round(house_atten, 1))
    target_mag_path = f'{lspk_folder}/target_mag_{suffix}.dat'
    target_pha_path = f'{lspk_folder}/target_pha_{suffix}.dat'

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
    try:
        from scipy.signal import hilbert
        eq_pha = np.angle( ( hilbert( np.abs( 10**(eq_mag/20) ) ) ) )    
    # if you have not scipy signal installed, you can just use zeros:
    except:
        eq_pha = np.zeros(len(freq))

    # Write data to file
    np.savetxt (target_mag_path, eq_mag)
    np.savetxt (target_pha_path, eq_pha)
    print( f'Target curves stored at:\n{target_mag_path}\n{target_pha_path}' )

    try:
        import matplotlib.pyplot as plt
        do_plot()
    except:
        print ( 'cannot pyplot' )
