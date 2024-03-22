import os
import stat

from select import select
from log import log

class Pipe():
    _path = None
    _data = None
    def __init__(self, path : str, sub_type : str):
        if sub_type[0] == 'r':
            typ = 0
        elif sub_type[0] == 'w':
            typ = 1
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

    def get_path(self):
        return self._path

    def get_data(self):
        return self._data
        
    def write(self, datas : str):
        try:
            if os.path.exists(self._path):
                if stat.S_ISFIFO(os.stat(self._path).st_mode):
                    with open(self._path, 'w') as fifo:
                        fifo.write(f"{datas}-")
        except Exception as e:
            print(e)

    def read(self):
        try:
            with open(self._path, 'r') as fifo:
                select([fifo],[],[fifo])
                self._data = fifo.read()
                if self._data == '':
                    return False
                else:
                    return True
        except Exception as e:
            print(e)
        
    def cleanup(self):
        os.unlink(self._path)