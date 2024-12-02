"""
    tests.utils
    ~~~~~~~~~~~

    test utilities

    :created: 2024-12-02
"""

import os
from os.path import abspath, dirname, join

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
