"""
    tests.test_sliding_window
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    unit tests for redis sliding window command

    :created: 2024-12-02
"""

import time
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
    """Tests in this class are using 'real' Redis server time"""

    def test_w1000_b0_roundtrip(self):

        rdsconn = self.rdsconn
        sliding_window_cmd = rdsconn.sliding_window

        # main window: no more than 4 requests in 1 s
        window = WindowDef(size_ms=1_000, limit=4)

        # use the command 5 times
        # we shall succeed 4 times (status=0) and fail 1 time (status=1)
        for pos, expect in enumerate([0, 0, 0, 0, 1]):
            actual = sliding_window_cmd(TEST_KEY, window, ttl_msec=1_010)
            self.assertEqual(actual, expect, f"failed assertion #{pos}")

    def test_w10000_b100_roundtrip(self):

        rdsconn = self.rdsconn
        sliding_window_cmd = rdsconn.sliding_window

        # main window: no more than 12 requests in 10 s
        window = WindowDef(size_ms=10_000, limit=12)

        # burst limit: no more than 4 requests in 50 ms
        burst_limit = WindowDef(size_ms=50, limit=4)

        status_groups = [
            # status indicates which window has failed
            # 1 -> 'main' window
            # 2 -> burst limit
            [0, 0, 0, 0, 2],
            [0, 0, 0, 0, 2],
            [0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1],
        ]

        for gn, expects in enumerate(status_groups):
            for pos, expect in enumerate(expects):
                actual = sliding_window_cmd(
                    TEST_KEY, window, burst_limit, ttl_msec=10_100
                )
                self.assertEqual(actual, expect, f"failed assertion #{gn}-{pos}")
            time.sleep(0.060)

    def test_w100_b0_pipeline(self):

        rdsconn = self.rdsconn
        sliding_window_cmd = rdsconn.sliding_window

        # main window: no more than 4 requests in 100 ms
        window = WindowDef(size_ms=100, limit=4)

        # set redis cmd pipe
        ppl = rdsconn.pipeline()
        for _ in range(5):
            sliding_window_cmd(TEST_KEY, window, ttl_msec=110, pipe_to=ppl)
        resp = ppl.execute()
        self.assertEqual(resp, [0, 0, 0, 0, 1])

    def test_w1000_b10_pipeline(self):

        rdsconn = self.rdsconn
        sliding_window_cmd = rdsconn.sliding_window

        # main window: no more than 16 requests in 1 sec
        window = WindowDef(size_ms=1_000, limit=16)

        # burst limit: no more than 4 requests in 10 ms
        burst_limit = WindowDef(size_ms=10, limit=4)

        status_groups = [
            # status indicates which window has failed
            # 1 -> 'main' window
            # 2 -> burst limit
            [0, 0, 0, 0, 2],
            [0, 0, 0, 0, 2],
            [0, 0, 0, 0, 2],
            [0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1],
        ]

        for gn, expects in enumerate(status_groups):
            ppl = rdsconn.pipeline()
            for _ in expects:
                sliding_window_cmd(
                    TEST_KEY, window, burst_limit, ttl_msec=1_010, pipe_to=ppl
                )
            self.assertEqual(ppl.execute(), expects, "failed assertion #{gn}")
            time.sleep(0.015)

    def test_expires(self):

        rdsconn = self.rdsconn
        sliding_window_cmd = rdsconn.sliding_window

        # main window: no more than 1 requests in 50 ms
        window = WindowDef(size_ms=50, limit=1)

        actual = sliding_window_cmd(TEST_KEY, window, ttl_msec=55)
        self.assertEqual(actual, 0, f"failed assertion")

        time.sleep(0.060)
        ttl = rdsconn.pttl(TEST_KEY)
        self.assertFalse(rdsconn.exists(TEST_KEY), f"TEST_KEY still up for {ttl} ms")

    def test_teardown(self):

        # make sure that TEST_KEY is not in redis
        self.assertFalse(self.rdsconn.exists(TEST_KEY))
