import doctest
import unittest

from structurefinder.searcher import database_handler, cif_file
from shelxfile import shelx, misc


class DoctestsTest(unittest.TestCase):
    def test_run_doctest(self):
        print('\n')
        for name in [shelx, misc, database_handler, cif_file]:
            failed, attempted = doctest.testmod(name)  # , verbose=True)
            if failed == 0:
                print('passed all {} tests in {}!'.format(attempted, name.__name__))
            else:
                msg = '!!!!!!!!!!!!!!!! {} of {} tests failed in {}  !!!!!!!!!!!!!!!!!!!!!!!!!!!'.format(failed,
                                                                                                         attempted,
                                                                                                         name.__name__)
                self.assertFalse(failed, msg)
