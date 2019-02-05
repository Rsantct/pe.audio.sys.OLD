See here: 

    https://github.com/AudioHumLab/FIRtro/wiki/04a-Instalación-de-Linux-y-paquetes-de-SW

Usually it is enough to integrate the user wich will run pre.di.c into convenient groups:

    sudo usermod -a -G cdrom,audio,video,plugdev yourUser

Also check you have the following summary of packages on your linux installation:

```
    alsa-utils
    jackd2
    brutefir
    ecasound ecatools python-ecasound ladspa-sdk fil-plugins
    zita-ajbridge zita-njbridge
    apache2
    mpd mpc
```

## Python 3 on Raspberry Pi Raspbian

We need Pyton >=3.6, but currently Raspbian is based on Debian *stretch* that comes with Python 3.5. Hope Raspbian updates to Debian *buster* soon.

### Python 3.6.x from sources

https://tutorials.technology/tutorials/67-Installing-python-36-on-raspberrypi.html

    sudo apt-get update

    sudo apt-get install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev

    mkdir tmp

    cd tmp

    wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz

    tar xf Python-3.6.5.tar.xz

    cd Python-3.6.5

    ./configure --enable-optimizations

    make

Now, optionally you can resume reading a dozen of chapters of your favourite book :-)

    sudo make altinstall

    sudo pip3 install --upgrade pip

You are done. Remove your `tmp/` stuff

Removing above packages used for building does not worth it, immo.

### Berryconda
I've found Berryconda, a Python3.6 distro for Raspbian based in the well known Python distribution Anaconda that works well.

https://github.com/jjhelmus/berryconda


    Do you wish the installer to prepend the Berryconda3 install location
    to PATH in your /home/predic/.bashrc ? [yes|no]
    [no] >>> yes

I've found that it is needed to move the following `~/.bashrc` added lines to your `~/.profile`

    # added by Berryconda3 installer
    export PATH="/home/predic/berryconda3/bin:$PATH"

