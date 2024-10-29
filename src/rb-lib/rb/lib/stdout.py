import contextlib
import io
import sys
from io import StringIO
from typing import Callable, Generator


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


def capture_stdout_as_generator(
    func: Callable, *args, **kwargs
) -> Generator[str, None, None]:
    stdout_buffer = io.StringIO()
    with contextlib.redirect_stdout(stdout_buffer):
        func(*args, **kwargs)

    # Go to the start of the buffer and yield each line
    stdout_buffer.seek(0)
    for line in stdout_buffer:
        yield line
