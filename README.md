# Dinosaur in a Box!!!!
Scott Baker, http://www.smbaker.com/

This project is a simple raspberry pi zero w, with a button, a led, and an adafruit stereo
bonnet. The LED flashes continuously to attract toddlers. When a toddler presses a button,
it will play a random dinosaur sound effect.

## Automatic Shutdown

Automatic shutdown uses the circuit described at https://www.raspberrypi.org/forums/viewtopic.php?t=145954.

GPIO 4 is configured as a poweroff signal by adding `dtoverlay=gpio-poweroff,gpiopin=4` to /boot/config.txt.
A capacitor is charged and when that capaictor reaches the threshold necessary to energize a transistor,
the EN pin on the DC/DC converter is pulled low. The capacitor can be discharged by either pressing the
button or by the pi pulling GPIO4 low (via the gpio-poweroff overlay).

Automatic shutdown is enabled by passing the `--autoshutdown` command line option.
