"""
    tests.test_sliding_window
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    unit tests for redis sliding window command

    :created: 2024-12-02
"""
import unittest

from .utils import load_lua_command

class TestUtils(unittest.TestCase):

    def test_load_lua_command(self):
        cmd = load_lua_command("sliding_window.lua")
        self.assertTrue(len(cmd) > 0)


