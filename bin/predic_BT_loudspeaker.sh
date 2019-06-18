#!/bin/bash

# This script starts the necessary jack to PA ports and the PA loopack,
# in order to use a BT loudspeaker under PA as a predic input follower

# It is needed that BT loudspeaker is paired and available under PA.

# Remember you need to declare the jack to PA ports 'pulse_source' inside 
# the 'jack_monitors:' section under <config.yml>


# Stopping 
~/pre.di.c/init/pulseaudio-jack-source+loopback stop
sleep 1

# Starting
~/pre.di.c/init/pulseaudio-jack-source+loopback start &
sleep 3

# Reconnecting the current input in order to reach the new monitor ports
input=$(grep input ~/pre.di.c/config/state.yml | cut -f2 -d' ')
control input $input
