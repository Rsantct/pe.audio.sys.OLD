#!/bin/bash

# (i) You need to have the executable jackminimix
#     Visit https://www.aelius.com/njh/jackminimix/ to download and compile
#     If you use armhf machine like a Raspberry Pi we provide the binary here:
#       pe.audio.sys/pre.di.c/doc/armhf_binaries/jackminimix

################## USER SETTINGS #########################3
#
# SOURCES (space separated portNames w/o the _N suffix)
sources=( system:capture )
#
# UDP PORT: 
port=9995
#
##########################################################

# Somo help
if [[ $1 == *'-h'* ]]; then
    echo
    echo 'Starts jackminimix and connects sources, e.g.:'
    echo
    echo '  pre.di.c    --->    in1'
    echo '  system      --->    in2'
    echo
    echo '  - Option  -i  will insert the mixer'
    echo '    between pre.di.c and the sound card.'
    echo
    echo '  - Sources to be connected to mixer inputs'
    echo '    can be configured inside this script.'
    echo
    exit 0
fi

# Stops if running
killall -KILL jackminimix
sleep 1

# Number of mixer inputs = number of sources + 2
# This way in1 will be used if inserting is desired
# also the last inX will be free for the user.
numberOfInputs=${#sources[@]}
((numberOfInputs+=2))

# Starts the mixer
jackminimix -v -p $port -c $numberOfInputs &

# Wait until 2 seconds for mixer ports to be available on jack
n=0
while true; do
    ports=$(jack_lsp minimixer:out_right)
    if [[ $ports ]]; then
        break
    fi
    sleep .2
    ((n++))
    if [[ $n -gt 10 ]]; then
        echo "Jackminimixer ports not detected"
        exit -1
    fi
done

# Connect sources to the mixer from 'in2' on
echo "(i) [minimixer:in1] is reserved for inserting pre.di.c"
N=2
for source in "${sources[@]}"; do

    echo "(i) connecting [$source] to [minimixer:in$N]"
    jack_connect    "$source"_1 minimixer:in"$N"_left
    jack_connect    "$source"_2  minimixer:in"$N"_right
    
    # Adjust inputs gain to 0 dB:
    ~/bin/jackminimix_ctrl.py -i"$N" -g0

    ((N++))
done
echo "(i) [minimixer:in"$N"] is free"
~/bin/jackminimix_ctrl.py -i"$N" -g0

# If inserting is desired
if [[ $1 == *'-i'* ]]; then

    echo "(i) inserting the mixer:  pre.di.c --> in1"
    echo "                          out      --> system:playback"
    ~/pre.di.c/clients/jackminimix_insert.sh

else

    # Set as the pre.di.c input source
    echo "input minimixer" | nc -N localhost 9999

fi

# Shows the mixer connections:
jack_view_connections.py minimixer
