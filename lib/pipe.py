import os
import stat

from select import select
from core import log


class Pipe():
    _path = None
    _data = None

    _fifo = None


    def __init__(self, path : str, sub_type : str):
        if sub_type[0] == 'r':
            type = 0
        elif sub_type[0] == 'w':
            type = 1
        else:
            log.err("Wrong arguments in class inisialization: class Pipe()")
            raise Exception("bob-core/no correct arguments specified")

        if os.path.exists(path):
            if not stat.S_ISFIFO(os.stat(path).st_mode):
                os.remove(path)
                os.mkfifo(path)
        else:
            os.mkfifo(path)

        self._path = path
        
        if type == 0:
            self._fifo = os.open(path, os.O_RDONLY)
        else:
            self._fifo = os.open(path, os.O_WRONLY)


    def get_path(self):
        return self._path


    def get_data(self):
        return self._data
        

    def write(self, datas : str):
        try:
            os.write(self._fifo, f"{datas}-".encode())
        except Exception as e:
            log.err(f"FIFO (Pipe class): {e}")


    def read(self):
        try:
            self._data = os.read(self._fifo, 100)
            return self._data.decode()
        except Exception as e:
            log.err(f"FIFO (Pipe class): {e}")
        

    def cleanup(self):
        os.close(self._fifo)
        os.unlink(self._path)
