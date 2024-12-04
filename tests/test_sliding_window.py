"""
    tests.test_sliding_window
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    unit tests for redis sliding window command

    :created: 2024-12-02
"""

import unittest

from .utils import add_sliding_window_cmd, redis_connect, WindowDef

TEST_KEY = "not_used_elsewhere"


class TestRedisConn(unittest.TestCase):
    """Open redis connection and add sliding_window lua cmd wrapper"""

    @classmethod
    def setUpClass(cls):
        cls.rdsconn = add_sliding_window_cmd(redis_connect())

    def tearDown(self):
        resp = self.rdsconn.delete(TEST_KEY)

    @classmethod
    def tearDownClass(cls):

        # Close connection
        cls.rdsconn.close()


class TestSlidingWindow(TestRedisConn):

    def test_one_window_roundtrip(self):

        rdsconn = self.rdsconn
        sliding_window_cmd = rdsconn.sliding_window

        # 1 second window with limit 4
        window = WindowDef(size_ms=1_000, limit=4)

        # use the command 5 times
        # we shall succeed 4 times (status=0) and fail 1 time (status=1)
        for pos, expect in enumerate([0, 0, 0, 0, 1]):
            actual = sliding_window_cmd(TEST_KEY, window)
            self.assertEqual(actual, expect, f"failed assertion #{pos}")

    def test_one_window_pipeline(self):

        rdsconn = self.rdsconn
        sliding_window_cmd = rdsconn.sliding_window

        # 1 second window with limit 4
        window = WindowDef(size_ms=1_000, limit=4)

        # set redis cmd pipe
        ppl = rdsconn.pipeline()
        for _ in range(5):
            sliding_window_cmd(TEST_KEY, window, pipe_to=ppl)
        resp = ppl.execute()
        self.assertEqual(resp, [0, 0, 0, 0, 1])

    def test_teardown(self):

        # make sure that TEST_KEY is not in redis
        self.assertFalse(self.rdsconn.exists(TEST_KEY))
