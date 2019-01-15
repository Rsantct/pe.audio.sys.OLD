#!/bin/bash

################## USER SETTINGS #########################3
#
# UDP PORT: 
port=9995
#
# SOURCES (space separated portNames w/o the _N suffix)
sources=( system:capture alsa_loop:output )
#
##########################################################


# Somo help
if [[ $1 == *'-h'* ]]; then
    echo 'Starts jackminimix and connects clients, e.g.:'
    echo '  system      --->    in1'
    echo '  alsa_loop   --->    in2'
    exit 0
fi

# Stops if running
killall -KILL jackminimix
sleep 1

# Starts the mixer,
# number of mixer inputs <= number of sources
numberOfInputs=${#sources[@]}
jackminimix -v -p $port -c $numberOfInputs &
sleep 1

# Connect sources to the mixer
N=1
for source in "${sources[@]}"; do

    echo "connecting [$source] to [minimixer:in$N]"
    jack_connect    "$source"_1 minimixer:in"$N"_left
    jack_connect    "$source"_2  minimixer:in"$N"_right
    # channel gain to 0 dB:
    ~/pre.di.c/clients/bin/jackminimix_ctrl.py -i"$N" -g0

    ((N++))
done

# Set as the pre.di.c input source
echo "input minimixer" | nc -N localhost 9999
