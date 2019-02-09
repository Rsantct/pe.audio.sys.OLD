#!/bin/bash

# User script to reconfigure speaker.yml with one of the 
# available target curves under the speaker folder, 
# then order pre.di.c to refresh the target EQ on runtime.

lspks_folder=$HOME/pre.di.c/loudspeakers/
tmp=$(grep ^loudspeaker: $HOME/pre.di.c/config/config.yml)
lspk=$(echo $tmp | cut -d' ' -f2)

# Somo help
if [[ ! $1 ]]; then
    echo
    echo User script to reconfigure speaker.yml with one of the 
    echo available target curves under the speaker folder, 
    echo then order pre.di.c to refresh the target EQ on runtime.
    echo
    echo Please add a pattern to identify the desired target.
    echo
    exit 0
fi

cd "$lspks_folder""$lspk"

# Iterate over target files
for f in *target_*; do

    # If pattern matchs
    if [[ "$f" == *"$1"* ]]; then

        # updates mag curve inside speaker.yml
        if [[ "$f" == *"target_mag"* ]];then
            echo setting: $f
            sed -i -e "/target_mag_curve:/c\target_mag_curve:\ ""$f"  \
                   "$lspks_folder""$lspk"/speaker.yml
        fi

        # updates pha curve
        if [[ "$f" == *"target_pha"* ]];then
            echo setting: $f
            sed -i -e "/target_pha_curve:/c\target_pha_curve:\ ""$f"  \
                   "$lspks_folder""$lspk"/speaker.yml
        fi
    fi

done

# Finally, orders pre.di.c to reload the new curves:
echo "reload_target" | nc -N localhost 9999
