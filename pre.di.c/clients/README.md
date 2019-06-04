
## pre.di.c/clients/

Must locate here any code to be intended as a **client** or **auxiliary** feature from the point of view of **pre.di.c**, for instance:

- **www/** the control web page and related web **macros** scripts
- **bin/players.py** a module to interface with players
- **bin/aux.py** a module to interface with local functions
- the global idea: anything which is designed to be plugged to work with the pre.di.c kernel

Be aware that **end user scripts** and similar stuff must go inside [your home ~/bin folder](https://github.com/Rsantct/pe.audio.sys/tree/master/bin)


As per **pre.di.c** wants to run this clients, you must update your `PYTHONPATH` env variable for instance by editing your **`.profile`** home file:
```
export PYTHONPATH="$PYTHONPATH:$HOME/pre.di.c/bin:$HOME/pre.di.c/clients/bin"
```

### pre.di.c/clients/bin/players.py

This module is used from a server to retrieve the played track metadata and also for controlling the available players (mplayer, mpd, spotify)

If disk / tracks information is desired for CD audio, it is needed to install the 'cdcd' linux package.
