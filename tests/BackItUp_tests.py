from nose.tools import assert_equal
from cStringIO import StringIO
import BackItUp


def setup():
    print "SETUP!"


def teardown():
    print "TEAR DOWN!"


def test_basic():
    print "I RAN!"
