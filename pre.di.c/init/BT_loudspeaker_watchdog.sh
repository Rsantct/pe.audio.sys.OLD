#!/bin/bash

# This script starts or stops the necessary jack to PA ports and the PA loopack,
# in order to use a BT loudspeaker under PA as a pre.di.c input monitor,
# under a Desktop installation of pre.di.c

# Remember you need to declare the jack to PA ports 'pulse_source' inside
# the 'jack_monitors:' section under <config.yml>

###############################################################
# Default BT loudspaker address, or read it from command line:
BTaddr=00:0C:8A:E1:F8:89
###############################################################


if [ $1 ]; then
  BTaddr=$1
fi
BTaddr=${BTaddr//:/_}
BTsink="bluez_sink."$BTaddr".a2dp_sink"

# Watchdog that checks if the BT loudspeaker is available under the PA user session:

started=no

while true; do

    tmp=$(pactl list sinks short | grep $BTsink)

    if [[ $tmp ]]; then

        if [[ $started == no ]]; then
            # Starting
            echo '(i) BT loudspeaker is available under Pulseaudio, '
            echo '    connecting as a pre.di.c input monitor'
            ~/pre.di.c/init/pulseaudio-jack-source+loopback start $BTaddr &
            sleep 3
            # Reconnecting the current input in order to reach the new monitor ports
            input=$(grep input ~/pre.di.c/config/state.yml | cut -f2 -d' ')
            control input $input

            started=yes
        fi

    else
        if [[ $started == yes ]]; then
            # Stopping
            echo '(i) BT loudspeaker not available under Pulseaudio'
            ~/pre.di.c/init/pulseaudio-jack-source+loopback stop

            started=no
        fi
    fi

    sleep 5

done
