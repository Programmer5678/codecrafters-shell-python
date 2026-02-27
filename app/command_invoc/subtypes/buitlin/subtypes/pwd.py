from app.command_invoc.models import FutureShellContext
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc

from multiprocessing import Process
import os

def runny(spec, shell_context):
    os.write(1, (shell_context.cwd() + "\n").encode())


class ShellContextUpdate:
    def __init__(self, value, is_update):
        self._value = value
        self._is_update = is_update

    @classmethod
    def no_update(cls):
        return cls(None, False)

    @classmethod
    def new(cls, value):
        return cls(value, True)

    def is_update(self):
        return self._is_update

    def value(self):
        return self._value
        
class Runner:
    
    def __init__(self, spec, shell_context):
        self._spec = spec
        self._shell_context = shell_context
        self._updated_end_shell_context = ShellContextUpdate.no_update()
        
    def start(self):
        res = runny(self._spec, self._shell_context)
        if res != None:
            self._updated_end_shell_context = ShellContextUpdate.new( res )        
        
    def updated_end_shell_context(self):
        return self._updated_end_shell_context

class PwdCommand(BuiltinCommandInvoc):
    expected_command = "pwd"

    def run_core(self):
        runner = Runner(self.spec(), self.shell_context())
        return runner
