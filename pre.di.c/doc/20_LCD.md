# LCD for pre.di.c

# Get the LCD hardware

See here:
https://github.com/AudioHumLab/FIRtro/wiki/855-Display-LCD


# The software

    apt list lcdproc

If version >= 0.5.6, then

    apt install lcdproc

If not: see how to compile in the link above.

## usb4all needs USB permissions

Prepare `/etc/udev/rules.d/50-usb.rules`

    # allow access to usb devices for users in dialout group
    SUBSYSTEM=="usb", MODE="0666", GROUP="dialout"

And include your user into the `dialout` group:

    sudo usermod -G dialout -a predic

**Reboot the machine**

## Testing the LCD

(i) Please edit and uncomment the appropiate driver line for your machine arch:

    $ nano pre.di.c/clients/lcd/LCDd.conf

Try to start the server:

    $ LCDd -c pre.di.c/clients/lcd/LCDd.conf

Test the standard packaged client:

    $ lcdproc -f  &
    
    $ killall lcdproc      # to stop the show

## Enabling pre.di.c info on the LDC display

Enable a `lcd` line into the init scripts configuration file `config/init`.
