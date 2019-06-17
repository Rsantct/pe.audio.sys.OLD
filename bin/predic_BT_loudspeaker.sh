#!/bin/bash

input=$(grep input ~/pre.di.c/config/state.yml | cut -f2 -d' ')

~/pre.di.c/init/pulseaudio-jack-source+loopback stop
sleep 1

~/pre.di.c/init/pulseaudio-jack-source+loopback start & sleep 3; control input $input
