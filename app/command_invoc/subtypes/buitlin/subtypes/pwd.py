from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc

from multiprocessing import Process
import os

def runny(spec, shell_context):
    os.write(1, (shell_context.cwd() + "\n").encode())
    return shell_context


class Runner:
    
    def __init__(self, spec, shell_context):
        self._spec = spec
        self._shell_context = shell_context
        self._future_shell_context = None
        
    def start(self):
        self._future_shell_context = runny(self._spec, self._shell_context)
        
    def future_shell_context(self):
        return self._future_shell_context


class PwdCommand(BuiltinCommandInvoc):
    expected_command = "pwd"

    def run_core(self):
        runner = Runner(self.spec(), self.shell_context())
        return runner
