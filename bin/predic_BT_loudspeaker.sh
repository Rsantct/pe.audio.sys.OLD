#!/bin/bash

# This script starts the necessary jack to PA ports and the PA loopack,
# in order to use a BT loudspeaker under PA as a predic input monitor,
# under a Desktop installation.

# The BT loudspeaker must be paired and available under the PA user session.

# Remember you need to declare the jack to PA ports 'pulse_source' inside 
# the 'jack_monitors:' section under <config.yml>

# (i) Configure here the BT loudspeaker address or give it as argument
BTaddr=00:0C:8A:E1:F8:89

if [ $1 ]; then
  BTaddr=$1
fi

# Stopping 
~/pre.di.c/init/pulseaudio-jack-source+loopback stop
sleep 1

# Starting
~/pre.di.c/init/pulseaudio-jack-source+loopback start $BTaddr &
sleep 3

# Reconnecting the current input in order to reach the new monitor ports
input=$(grep input ~/pre.di.c/config/state.yml | cut -f2 -d' ')
control input $input
