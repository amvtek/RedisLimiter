"""
    tests.test_sliding_window
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    unit tests for redis sliding window command

    :created: 2024-12-02
"""
import unittest

from .utils import load_lua_command, redis_connect

class TestSlidingWindow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # Open redis connection
        rdsconn = redis_connect()

        # Add sliding_window command to rdsconn
        scriptsrc = load_lua_command("sliding_window.lua")
        sliding_window = rdsconn.register_script(scriptsrc)
        rdsconn.sliding_window = sliding_window

        cls.rdsconn = rdsconn

    def test_provisional(self):

        # we use 5 second window with limit 2

        # first 2 calls shall be allowed (rc == 0)
        rc0 = self.rdsconn.sliding_window(keys=["testkey"], args=[0, 10_000, 5_000, 2])
        self.assertEqual(rc0, 0, "failed first call")
        rc1 = self.rdsconn.sliding_window(keys=["testkey"], args=[0, 10_000, 5_000, 2])
        self.assertEqual(rc1, 0, "failed second call")

        # third call shall not be allowed (rc == 1)
        rc2 = self.rdsconn.sliding_window(keys=["testkey"], args=[0, 10_000, 5_000, 2])
        self.assertEqual(rc2, 1, "failed third call")

    @classmethod
    def tearDownClass(cls):

        # Close connection
        cls.rdsconn.close()
