
## pre.di.c/clients/

Must locate here any code to be intended as a **client** or **auxiliary** feature from the point of view of **pre.di.c**, for instance:

- **players.py** a module to interface with players (MPD, Spotify, CD-Audio, DVB-T, internet)
- **aux.py** a module to interface with local functions
- **www/** the control web page and related web **macros** scripts
- **lcd/** files to run the LCD service
- the global idea: anything which is designed to be plugged to work with the pre.di.c kernel

If the client or auxiliary feature consists of several files, you can keep all of them together in a subfolder, this is the case of the web page stuff under  **`pre.di.c/clients/www/`** or the LCD stuff under **`pre.di.c/clients/lcd/`**

Be aware that **end user scripts** and similar stuff must go inside **[your home ~/bin folder](https://github.com/Rsantct/pe.audio.sys/tree/master/bin)**


As per **pre.di.c** wants to run this clients, you must update your `PYTHONPATH` env variable for instance by editing your **`.profile`** home file:
```
export PYTHONPATH="$PYTHONPATH:$HOME/pre.di.c/bin:$HOME/pre.di.c/clients"
```

### pre.di.c/clients/players.py

This module is used from a server to retrieve the played track metadata and also for controlling the available players (mplayer, mpd, spotify)

#### CD AUDIO
If disk/tracks information is desired for CD audio, it is needed to install the **`cdcd`** linux package, and run it manually in order to autoconfigure it. Be sure the generated `~/.cdserverrc` have `ACCESS=SERVER` in order to query remote cddb databases.

<image alt="CD Audio" src="https://github.com/Rsantct/pe.audio.sys/blob/master/pre.di.c/clients/www/images/control%20web%202.1%20CDAudio_a.jpg" width="300"/>

<image alt="CD Audio" src="https://github.com/Rsantct/pe.audio.sys/blob/master/pre.di.c/clients/www/images/control%20web%202.1%20CDAudio_b.jpg" width="300"/>
