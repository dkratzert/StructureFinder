import doctest
import unittest

import searcher
import strf
from misc import update_check
from searcher import database_handler, fileparser
from shelxfile import shelx, elements, misc


class DoctestsTest(unittest.TestCase):
    def test_run_doctest(self):
        for name in [strf, shelx, elements, misc, searcher, update_check, database_handler,
                     fileparser, searcher.misc]:
            failed, attempted = doctest.testmod(name)  # , verbose=True)
            if failed == 0:
                print('passed all {} tests in {}!'.format(attempted, name.__name__))
            else:
                msg = '!!!!!!!!!!!!!!!! {} of {} tests failed in {}  !!!!!!!!!!!!!!!!!!!!!!!!!!!'.format(failed,
                                                                                                         attempted,
                                                                                                         name.__name__)
                self.assertFalse(failed, msg)