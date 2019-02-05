See here: 

https://github.com/AudioHumLab/FIRtro/wiki/04a-Instalación-de-Linux-y-paquetes-de-SW

Usually it is enough to integrate the user wich will run pre.di.c into convenient groups:

    sudo usermod -a -G cdrom,audio,video,plugdev yourUser

Also check you have the following summary of packages on your linux installation:

    alsa-utils jackd2 brutefir ecasound ecatools python-ecasound ladspa-sdk fil-plugins zita-ajbridge zita-njbridge apache2 mpd mpc

## Python 3 on Raspberry Pi Raspbian

We need Pyton >=3.6, but currently Raspbian is based on Debian *stretch* that comes with Python 3.5. Hope Raspbian updates to Debian *buster* soon.

### option 1: Python 3.6.x from sources

https://realpython.com/installing-python/#compiling-python-from-source

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
... **about 3 h later**:

    sudo make altinstall

You are done, but now you have both 3.5 and 3.6 (under /usr/local).

Your python3 stills points to 3.5:

    $ ls -lh /usr/bin/python3*
    lrwxrwxrwx 1 root root    9 Jan 20  2017 /usr/bin/python3 -> python3.5
    -rwxr-xr-x 2 root root 3.8M Sep 27 19:25 /usr/bin/python3.5
    -rwxr-xr-x 2 root root 3.8M Sep 27 19:25 /usr/bin/python3.5m
    lrwxrwxrwx 1 root root   10 Jan 20  2017 /usr/bin/python3m -> python3.5m
    
    $ ls /usr/local/bin/pip*
    /usr/local/bin/pip3.6

Replace it to 3.6:

    $ sudo rm /usr/bin/python3
    $ sudo ln -s /usr/local/bin/python3.6 /usr/bin/python3
    $ sudo ln -s /usr/local/bin/pip3.6 /usr/local/bin/pip3


To `pip3` to avoid `lsb_release` errors, google searching proposes the following, and I have done it on my system :-/

    $ sudo mv /usr/bin/lsb_realease /usr/bin/lsb_realease.BAK

Finally remove your `tmp/` stuff.

Removing above packages used for building does not worth it, immo.

### option 2: Berryconda
I've found Berryconda, a Python3.6 distro for Raspbian based in the well known Python distribution Anaconda that works well.

https://github.com/jjhelmus/berryconda


    Do you wish the installer to prepend the Berryconda3 install location
    to PATH in your /home/predic/.bashrc ? [yes|no]
    [no] >>> yes

I've found that it is needed to move the following `~/.bashrc` added lines to your `~/.profile`

    # added by Berryconda3 installer
    export PATH="/home/predic/berryconda3/bin:$PATH"

