#!/bin/bash

# This script is intended as a generic frontend to control
# the volume of your monitor loudspeaker.

# Put here the path for the real script that controls your loudspeaker:
monitor_volume_path=~/pre.di.c/clients/PA_BT_lspk_monitor/PA_BT_volume.sh



volume=$1

if [[ $1 ]]; then
    $monitor_volume_path $volume
fi
