# -*- coding: utf-8 -*-
import atexit
import logging
import threading
import time

logger = logging.getLogger(__name__)


class ScreenRenderer(threading.Thread):

    def __init__(
        self, screen, frame_rate=60, queue=None,
        name='ScreenRenderer', group=None, verbose=None
    ):
        super(ScreenRenderer, self).__init__(
            name=name, group=group, verbose=verbose
        )
        self.__queue = queue
        self.__hw = screen
        self.__hw.begin()
        self.__last_render = 0
        self.__spf = 1.0 / float(frame_rate)
        self.__stop = threading.Event()

    def stop(self):
        logger.info('%s received STOP event', self.name)
        self.__stop.set()

    def run(self):
        logger.info(
            '%s started at %.3f seconds per frame', self.name, self.__spf
        )
        while 1:
            if self.__stop.is_set():
                logger.info('%s stopped', self.name)
                return
            now_ts = time.time()
            if now_ts - self.__last_render < self.__spf:
                continue
            self.__last_render = now_ts
            item = self.__queue.get()
            bitmap, row, col, col_count, col_offset = item
            self.__hw.display_block(
                bitmap, row, col, col_count, col_offset
            )
