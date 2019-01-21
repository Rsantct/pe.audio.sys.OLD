# LCD for pre.di.c

# Get the LCD hardware

See here:
https://github.com/AudioHumLab/FIRtro/wiki/855-Display-LCD


# The software

    apt list lcdproc

If version >= 0.5.6, 

    apt install lcdproc

If not: see how to compile on the above link.


Reboot the machine

## Testing the LCD

(i) Please uncomment the appropiate driver line for your machine arch:

    $ nano pre.di.c/clients/lcd/LCDd.conf

Try to start the server:

    $ LCDd -c pre.di.c/clients/lcd/LCDd.conf

Test the standard packaged client:

    $ lcdproc -f  &
    
    $ killall lcdproc      # to stop the show

## Enabling pre.di.c on the LDC

WORK IN PROGRESS
