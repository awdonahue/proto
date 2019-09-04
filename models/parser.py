from pathlib import Path

class Parser:
    """
    Parse binary files
    """
    def __init__(self, path: Path):
        self._filepath = path
        self._file_bytes = None
        self._total_bytes = 0

        self._read_file()

    def _read_file(self):
        fbytes = self._filepath.read_bytes()

        self._file_bytes = fbytes
        self._total_bytes = len(fbytes)
