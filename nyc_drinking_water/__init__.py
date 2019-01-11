import os
import sys

data_dir = os.path.abspath(os.path.dirname(__file__) + '/../data')
projection = 'EPSG:2260'

class HiddenPrints(object):
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, *args):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
