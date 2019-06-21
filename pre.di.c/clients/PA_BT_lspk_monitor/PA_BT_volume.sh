#!/bin/bash

# Will control the 1st BT loudspeaker found on Pulseaudio
BTaddr=$(~/pre.di.c/clients/PA_BT_lspk_monitor/PA_BT_1st_device.py)

if [[ $2 ]]; then
  BTaddr=$1
  volume=$2
else
  volume=$1
fi

BTaddr=${BTaddr//:/_}

if [[ $BTaddr == *"_"* ]]; then

    BTsink="bluez_sink."$BTaddr".a2dp_sink"
    echo Adjusting: $BTsink $volume
    pactl set-sink-volume $BTsink $volume

else
    echo "usage:  PA_BT_volume.sh  [xx:xx:...] volume"

fi

