See here: 

https://github.com/AudioHumLab/FIRtro/wiki/04a-Instalación-de-Linux-y-paquetes-de-SW

Usually it is enough:

- add the **`predic`** user to your system, this is optional so you can run pre.di.c under any existent user account if you want so.

    `sudo adduser predic`

- then integrate the user which will run pre.di.c into convenient groups:

    `sudo usermod -a -G cdrom,audio,video,plugdev YourUserHere`

Also install the following packages on your linux installation:

    sudo apt install alsa-utils libjack-jackd2-dev libasound2-dev libasound2-plugins
    sudo apt install jackd2 brutefir ecasound ecatools python-ecasound mpd mpc mplayer
    sudo apt install ladspa-sdk fil-plugins zita-ajbridge zita-njbridge apache2 libapache2-mod-php

