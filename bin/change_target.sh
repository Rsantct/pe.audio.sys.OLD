#!/bin/bash

if [[ ! $1 ]]; then
    echo please add a pattern to identify the desired target
    exit 0
fi

lspks_folder=/home/predic/pre.di.c/loudspeakers/

# YOUR LOUDSPEAKER
lspk=DynA42

cd "$lspks_folder""$lspk"

for f in *target_*; do

    if [[ "$f" == *"$1"* ]]; then

        if [[ "$f" == *"target_mag"* ]];then
            echo setting: $f
            sed -i -e "/target_mag_curve:/c\target_mag_curve:\ ""$f"  \
                   "$lspks_folder""$lspk"/speaker.yml
        fi

        if [[ "$f" == *"target_pha"* ]];then
            echo setting: $f
            sed -i -e "/target_pha_curve:/c\target_pha_curve:\ ""$f"  \
                   "$lspks_folder""$lspk"/speaker.yml
        fi
    fi

done
