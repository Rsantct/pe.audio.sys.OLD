#!/bin/bash

# Waiting for brutefir ports to be connected
t=30
while [[ $t>0 ]]; do

    bfports=$(jack_lsp -c brutefir | grep "^   ")
    if [[ $bfports ]];then
        break
    fi

    echo "(jack_minimix_insert) waiting for brutefir to be connected ("$t")"
    ((t--))
    sleep 1
done

# EXIT if t expires
if [[ "$t" -eq "0" ]];then
    echo "(jack_minimix_insert) CANCELLED because brutefir ports are not connected"
    exit -1
fi

# Inserts the mixer between pre.di.c and the soundcard
echo "(jack_minimix_insert) INSERTING jack_minimix"

echo "    disconnecting pre.di.c output from sound card"
jack_disconnect brutefir:fr.L   system:playback_1
jack_disconnect brutefir:fr.R   system:playback_2

echo "    connecting pre.di.c to mixer in1"
jack_connect    brutefir:fr.L   minimixer:in1_left
jack_connect    brutefir:fr.R   minimixer:in1_right

echo "    connecting the mixer output to the sound card"
jack_connect    minimixer:out_left  system:playback_1
jack_connect    minimixer:out_right system:playback_2
