"""
    tests.utils
    ~~~~~~~~~~~

    test utilities

    :created: 2024-12-02
"""

from os.path import abspath, dirname, join

projdir = dirname(dirname(abspath(__file__)))


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
