If you are interested on running a mixer for your jack sources, here we provided a jackminimix scripts for pre.di.c to work with.

    pre.di.c/clients/bin/jackminimix_start.sh
    pre.di.c/clients/bin/jackminimix_ctrl.py

**[jackminimix](https://www.aelius.com/njh/jackminimix/)**

jackminimix needs to be controlled via OSC protocol, unfortunately direct udp messages via netcat does not work for me,
so here we use `oscchief`, a nice OSC command line tool.

**[oscchief](https://github.com/hypebeast/oscchief)**

It is needed that you compile both `jackminimix` and `oscchief` tools under your ~/bin folder.

Here we provide armhf compiled binaries under this doc folder for your convenience.
