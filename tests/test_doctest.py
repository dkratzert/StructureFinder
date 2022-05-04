import doctest
import unittest

import searcher
import strf
from structurefinder.misc import update_check
from searcher import database_handler, fileparser
from structurefinder.shelxfile import shelx, elements
from structurefinder.shelxfile import misc


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