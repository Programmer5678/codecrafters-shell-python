class ShellContext:

    def __init__(self, cwd):
        self._cwd = cwd
        self._history = []

    def cwd(self):
        return self._cwd

    def history(self):
        return self._history

    def setcwd(self, cwd):
        self._cwd = cwd

    def add_line_history(self, line):
        self._history.append(line)