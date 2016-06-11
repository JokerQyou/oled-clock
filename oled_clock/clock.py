#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import threading
import time
from datetime import datetime

import gaugette.fonts
from gaugette.fonts import input_mono_24, tahoma_16

from base import Object

logger = logging.getLogger(__name__)


class ScreenClock(threading.Thread):
    """docstring for Screen"""
    def __init__(
        self, screen, frame_rate=20, sensor=None, queue=None,
        group=None, name='ScreenClock', verbose=None
    ):
        super(ScreenClock, self).__init__(
            group=group, name=name, verbose=verbose
        )
        self.__spf = 1.0 / float(frame_rate)
        self.__sensor = sensor
        self.__queue = queue
        self.__stop = threading.Event()

        # Clock related config
        self.__c = Object({
            'bitmap': screen.Bitmap(128, 64),
            'font': input_mono_24,
            'font_small': tahoma_16,
            'timestring': None,
            'datestring': None,
            'sensorstring': None,
        })

        # sensor related config
        self.__sr = Object({
            'last_read': 0,
            'last_value': None,
            'interval': 15,
        })

    def read_sensor(self, now=None):
        '''
        Read from sensor and return (temp, pressure, )
        Cached values are taken care of
        '''
        if now is None:
            now = time.time()
        c = self.__sr
        if now - c.last_read < c.interval and c.last_value is not None:
            return c.last_value

        temp = self.__sensor.read_temperature()
        pressure = self.__sensor.read_pressure()
        c.last_value = (temp, pressure, )
        c.last_read = now
        return c.last_value

    def draw_clock(self):
        '''Draw a clock to bitmap'''
        # Alias
        c = self.__c
        now_ts = time.time()
        now = datetime.fromtimestamp(now_ts)
        timestring = datetime.strftime(now, '%H:%M:%S')
        # No need to render again
        if c.timestring != timestring:
            # Draw the main clock
            # TODO we should only render the changed content
            time_text_width = c.bitmap.text_width(timestring, c.font)
            margin_left = (128 - time_text_width) / 2
            margin_top = (64 - c.font.char_height) / 2
            if c.timestring is not None:
                c.bitmap.clear_block(
                    margin_left, margin_top,
                    c.bitmap.text_width(c.timestring, c.font),
                    c.font.char_height
                )
            c.bitmap.draw_text(
                margin_left, margin_top, timestring, c.font
            )
            c.timestring = timestring

        # Draw date area is the top part of the screen
        datestring = datetime.strftime(now, '%m-%d')
        if c.datestring != datestring:
            # Draw the date string on the left
            margin_top = (margin_top - c.font_small.char_height) / 2
            c.bitmap.clear_block(
                0, margin_top,
                128, c.font_small.char_height
            )
            c.bitmap.draw_text(
                0, margin_top, datestring, c.font_small
            )
            # Draw day of the week on the right
            daywstring = datetime.strftime(now, '%A')
            margin_left = 128 - c.bitmap.text_width(daywstring, c.font_small)
            c.bitmap.draw_text(
                margin_left, margin_top, daywstring, c.font_small
            )
            c.datestring = datestring

        # Draw temperature at the bottom
        sensor_data = self.read_sensor(now_ts)
        sensorstring = '{:.1f}\177C'.format(sensor_data[0])
        if c.sensorstring != sensorstring:
            sr_text_width = c.bitmap.text_width(sensorstring, c.font_small)
            margin_left = 128 - sr_text_width
            margin_top = 64 - c.font_small.char_height
            if c.sensorstring is not None:
                previous_text_width = c.bitmap.text_width(
                    c.sensorstring, c.font_small
                )
                c.bitmap.clear_block(
                    128 - previous_text_width, margin_top,
                    previous_text_width, c.font_small.char_height
                )
            c.bitmap.draw_text(
                margin_left, margin_top,
                sensorstring, c.font_small
            )
            c.sensorstring = sensorstring

        # Render on hardware
        return 0, 0, 128, 0

    def stop(self):
        logger.info('%s received STOP event', self.name)
        self.__stop.set()

    def run(self):
        # Loop displaying a clock
        logger.info('Clock started at %.3f seconds per frame', self.__spf)
        while 1:
            if self.__stop.is_set():
                logger.info('%s stopped', self.name)
                return
            row, col, col_count, col_offset = self.draw_clock()
            self.__queue.put(
                (self.__c.bitmap, row, col, col_count, col_offset, )
            )
            time.sleep(self.__spf)

