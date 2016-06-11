#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import atexit
import os
import logging
from Queue import Queue
import threading

import gaugette.ssd1306
import Adafruit_BMP.BMP085 as BMP085

import screen
import clock

log_level = logging.DEBUG if os.environ.get('DEBUG', None) else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger()


def cleanup(screen):
    screen.reset()
    logger.info('Screen reset done')


def start_daemon():
    RST = int(os.environ.get('RST', '1'))
    DC = int(os.environ.get('DC', '0'))
    FPS = int(os.environ.get('FPS', '20'))

    QUEUE = Queue()
    SCREEN = gaugette.ssd1306.SSD1306(
        reset_pin=RST, dc_pin=DC, rows=64, cols=128
    )

    atexit.register(cleanup, SCREEN)
    logger.info('Cleanup function registered')

    SENSOR = BMP085.BMP085(mode=BMP085.BMP085_HIGHRES)
    CLOCK = clock.ScreenClock(
        SCREEN, frame_rate=FPS, sensor=SENSOR, queue=QUEUE
    )
    RENDERER = screen.ScreenRenderer(
        SCREEN, queue=QUEUE
    )
    RENDERER.daemon = True
    RENDERER.start()
    CLOCK.daemon = True
    CLOCK.start()
    while 1:
        try:
            CLOCK.join(1)
            if not CLOCK.is_alive():
                RENDERER.stop()
                break
        except KeyboardInterrupt:
            logger.info('Quiting...')
            RENDERER.stop()
            CLOCK.stop()
            raise SystemExit
    # TODO Add sensor and device file manager
    pass


if __name__ == '__main__':
    start_daemon()
