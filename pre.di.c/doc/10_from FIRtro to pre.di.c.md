# From FIRtro to pre.di.c

**NOTICE** that a predic loudspeaker folder is dedicated to some FS configuration, instead of FIRtro's subfolders filter structure for each running FS.

So 'fs' is no longer stored inside `config/state.yml`

**NOTICE** that pre.di.c uses YAML files, no longer .ini files are used.

       (i) PLEASE set your editor to tab by using 4 spaces

## PREPARING pre.di.c

- Make a folder for your loudspeaker an go inside:

```
    mkdir pre.di.c/loudspeakers/mylspkname
    cd pre.di.c/loudspeakers/mylspkname
```

- Copy here the provided file:

`cp   ../example2ways-sub/brutefir_settings.yml  .`

Edit and set your current FIR taps lenght, for example if your pcm files are 64K then FIRs are 16384 taps lenght:

```
    filter_length:      16384 # If your CPU supports it you can set for example 4096,4
    float_bits:         32
    overflow_warnings:  true
    allow_poll_mode:    false
    monitor_rate:       true
    powersave:          -80
    lock_memory:        true
    show_progress:      false
```

- Copy here your XO and DRC pcm files.

Run **`do_config_files.py -h`** for help on convention naming pcm files:

        XO:
          xo.someDescription.pcm

        DRC:
          drc.X_someDescription.pcm     Where X is the channel 'L' or 'R'

So forgot old `drc-1-L_xxxxx.pcm` naming from FIRtro, neither `drc` subfolders.

Copy all pcm stuff you will need here and rename pcm files as convenient. For example

```
    ls -1 *pcm > renaming

    nano renaming
    
        Edit here each line to somethin like:

        mv  lp-high.pcm                     xo.high_lp.pcm
        mv  drc-1-L_somodrcdescription.pcm  drc.L_somodrcdescription.pcm
        ... etc ...
        
    sh renaming
    rm renaming
    ls -1 *pcm
```

- Copy here the example target files:

    `cp  ../example2ways-sub/R20_ext*   .`

- Copy a template for the loudspeaker definition

    `cp  ../example2ways-sub/example2ways-sub.yml  mylspkname.yml`
    
    Please keep 'mylspkname' the same name you've used for your loudspeaker folder.
    
Then edit `mylspkname.yml` as convenient, for example:

```
fs: 44100
target_spl:     82
room_gain:      4.0
house_gain:     -2.0

drc_sets:
    multipV1:			drc.L_multipV1.pcm	drc.R_multipV1.pcm

xo_sets:

    mp:	
        lo:	
            fir:        xo.lo_mp.pcm         	xo.lo_mp.pcm         
            gain:       0.0                  	0.0                   
            delay_ms:   0.0                  	0.0                    
            polarity:   +1                   	+1                      
        hi:	
            fir:        xo.hi_mp.pcm         	xo.hi_mp.pcm    
            gain:       0.0                  	0.0                   
            delay_ms:   0.0                  	0.0                    
            polarity:   +1                   	+1                      

    lp:	
        lo:	
            fir:        xo.lo_lp.pcm         	xo.lo_lp.pcm         
            gain:       0.0                  	0.0                   
            delay_ms:   0.0                  	0.0                    
            polarity:   +1                   	+1                      
        hi:	
            fir:        xo.hi_lp.pcm         	xo.hi_lp.pcm    
            gain:       0.0                  	0.0                   
            delay_ms:   0.0                  	0.0                    
            polarity:   +1                   	+1               
```

    (target_spl, room_gain and house_gain settings have no effect, still...)

   
When you're done, you can generate the low level files needed for pre.di.c to work:

```
    cd ~
    do_config_files.py pre.di.c/loudspeakers/mylspkname
```

 
If all is right use `-w` to write down the candidate files.

- Review the output section under the new `brutefir_config` file

    `nano pre.di.c/loudspeakers/mylspkname/brutefir_config`

    Maybe you can re-use your FIRtro output section for convenient sound card mapping.
    
- Edit `pre.di.c/config/config.yml`
    
    Set properly:
    
```
loudspeaker: mylspkname    
system_card: hw:ALSAname,0
external_cards: ''
jack_options:          -R -ddummy -P8 -C2
```

    Leave jack dummy for now...

- Run pre.di.c

    `startaudio.py`