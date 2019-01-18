#!/bin/bash

# Inserts the mixer between pre.di.c and the soundcard

echo "disconnecting pre.di.c output from sound card"
jack_disconnect brutefir:fr.L   system:playback_1
jack_disconnect brutefir:fr.R   system:playback_2

echo "connecting pre.di.c to mixer in1"
jack_connect    brutefir:fr.L   minimixer:in1_left
jack_connect    brutefir:fr.R   minimixer:in1_right

echo "connecting the mixer output to the sound card"
jack_connect    minimixer:out_left  system:playback_1
jack_connect    minimixer:out_right system:playback_2
