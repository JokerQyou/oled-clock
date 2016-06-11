# oled clock

A simple clock on SSD1306 OLED screen.

Requirements stated in `requirements.txt` file.
Run `sudo python setup.py install` and you're done.

# Usage

* Set these env variables:
  * `RST` `wPi` number of the RESET pin your screen is using, defaults to `1` (
    BCM number `#18`).
  * `DC` `wPi` number of the DC pin your screen is using, defaults to `0` (BCM
    number `#17`).
  * `FPS` how many loops (at max) should the clock go through (to calculate time
    string, not to update the screen), defaults to 20.
* Run `sudo oclock`.

# License

BSD licens, see `LICENSE` file for details.
