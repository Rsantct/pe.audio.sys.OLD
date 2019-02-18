#!/usr/bin/env python3
""" just plots the curves from R20_ext-loudness_mag.dat
"""

import numpy as np
from matplotlib import pyplot as plt

import basepaths as bp
import getconfigs as gc

lmag = np.loadtxt(bp.config_folder + gc.config['loudness_mag_curves'])
freq = np.loadtxt(bp.config_folder + gc.config['frequencies'])

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)


for idx in range( lmag.shape[1] ):
    ax.semilogx ( freq, lmag[:,idx], label=idx)

ax.legend( loc="center", bbox_to_anchor=(1.15, 1.05) )
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1])

ax.set_title("R20_ext-loudness_mag.dat")

plt.show()


