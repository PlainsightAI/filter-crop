#!/usr/bin/env python

import logging
import multiprocessing
import os
import sys
import unittest

from filter_crop.filter import FilterCrop

logger = logging.getLogger(__name__)

logger.setLevel(int(getattr(logging, (os.getenv('LOG_LEVEL') or 'INFO').upper())))

VERBOSE   = '-v' in sys.argv or '--verbose' in sys.argv
LOG_LEVEL = logger.getEffectiveLevel()


class TestFilterCrop(unittest.TestCase):
    def test_filter_crop(self):
        if VERBOSE and LOG_LEVEL <= logging.WARNING:
            print()

        # TODO: test here

        pass


try:
    multiprocessing.set_start_method('spawn')  # CUDA doesn't like fork()
except Exception:
    pass

if __name__ == '__main__':
    unittest.main()
