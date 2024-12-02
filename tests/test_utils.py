"""
    tests.test_sliding_window
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    unit tests for redis sliding window command

    :created: 2024-12-02
"""
import unittest

from .utils import load_lua_command, redis_connect

class TestUtils(unittest.TestCase):

    def test_load_lua_command(self):
        cmd = load_lua_command("sliding_window.lua")
        self.assertTrue(len(cmd) > 0)

    def test_redis_connect(self):
        rdsconn = redis_connect()
        msg = "hello test"
        resp = rdsconn.echo(msg)
        self.assertTrue(resp == msg)


