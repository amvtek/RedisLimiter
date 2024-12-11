"""
    tests.utils
    ~~~~~~~~~~~

    test utilities

    :created: 2024-12-02
"""

import os
import secrets
from os.path import abspath, dirname, join
from typing import NamedTuple, Optional

import redis

projdir = dirname(dirname(abspath(__file__)))


def redis_connect() -> redis.Redis:
    """open redis connection reading parameters from process environment"""

    getenv = os.environ.get

    return redis.Redis(
        host=getenv("REDIS_HOST", "localhost"),
        port=int(getenv("REDIS_PORT", "6379")),
        db=int(getenv("REDIS_DB", "9")),
        decode_responses=True,
    )


class WindowDef(NamedTuple):
    size_ms: int
    limit: int


def add_sliding_window_cmd(rdsconn: redis.Redis) -> None:
    """add sliding_window command to rdsconn connection"""

    scriptsrc = load_lua_command("sliding_window.lua")
    callcmd = rdsconn.register_script(scriptsrc)

    # callcmd is low level
    # to ease its usage we expose it through a wrapper with named arguments
    def sliding_window(
        key: str,
        main_window: WindowDef,
        *burst_limits: WindowDef,
        extra_ttl_ms: Optional[int] = None,
        pipe_to: Optional[redis.client.Pipeline] = None,
    ):
        lua_args = []
        lua_args.extend(main_window)
        for bw in burst_limits:
            lua_args.extend(bw)
        if extra_ttl_ms is not None:
            lua_args.append(extra_ttl_ms)

        return callcmd(keys=[key], args=lua_args, client=pipe_to)

    rdsconn.sliding_window = sliding_window

    return rdsconn


def safe_key() -> str:
    """return random key"""
    token = secrets.token_hex(8).upper()
    return f"TEST-{token}"


class FileLoader:
    """helper class allowing to load content of resources files from base folder"""

    def __init__(self, root_path: str, mode: str = "r") -> None:
        self.root_path = root_path
        self.mode = mode

    def load(self, fpath: str) -> bytes | str:
        """load file at fpath

        Parameters
        ----------
        fpath:
            path relative to self.root_path of the to be loaded file

        Returns
        -------
            content of file at fpath
        """
        with open(join(self.root_path, fpath), self.mode) as f:
            return f.read()


load_lua_command = FileLoader(join(projdir, "redis")).load
