
## pre.di.c/clients/

Must locate here any code to be intended as a **client** or **auxiliary** feature from the point of view of **pre.di.c**, for instance:

- **www/** the control web page and related web **macros** scripts
- **players.py** a module to interface with players (for CDs it is needed the 'cdcd' linux package)
- **aux.py** a module to interface with local functions
- the global idea: anything which is designed to be plugged to work with the pre.di.c kernel

End user scripts and similar stuff must go inside [your home ~/bin folder](https://github.com/Rsantct/pe.audio.sys/tree/master/bin)


As per **pre.di.c** wants to run this clients, you must update your `PYTHONPATH` env variable for instance by editing your **`.profile`** home file:
```
export PYTHONPATH="$PYTHONPATH:$HOME/pre.di.c/bin:$HOME/pre.di.c/clients/bin"
```

