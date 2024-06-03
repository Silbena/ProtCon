import io
import time

class LogEntry:
    def __init__(self, line : int, msg : str) -> None:
        self.time = time.localtime()
        self.line = line
        self.msg = msg


class ConverterContext:
    def __init__(self, dst : io.IOBase, src : io.IOBase) -> None:
        self.errors : list[LogEntry] = []
        self.warnings : list[LogEntry] = []
        
        self.output = dst
        self.input = src

        self.current_line = 0

    def __iter__(self):
        for line in self.input:
            yield line
            self.current_line += 1

    def log_error(self, msg : str):
        self.errors.append(LogEntry(self.current_line, msg))

    def log_warning(self, msg : str):
        self.warnings.append(LogEntry(self.current_line, msg))

    def write(self, line : str):
        self.output.write(line)
    