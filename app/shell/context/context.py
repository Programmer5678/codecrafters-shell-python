class ShellContext:

    def __init__(self, cwd, start_history):
        self._cwd = cwd
        self._history = start_history
        self._new_history_start = len(start_history)
        self._history_session_start = len(start_history)

    def cwd(self):
        return self._cwd

    def history(self):
        return self._history

    def setcwd(self, cwd):
        self._cwd = cwd

    def add_line_history(self, line):
        self._history.append(line)
        
    def consume_new_history(self):
        result = self._history[ self._new_history_start: ]
        self._new_history_start = len(self._history)
        return result
    
    def session_history(self):
        return self._history[self._history_session_start : ]
        
        