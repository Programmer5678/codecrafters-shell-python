from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from multiprocessing import Process
import os


def runny(spec, shell_context):
    os.write(1, (" ".join(spec.args()) + "\n").encode())
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




class EchoCommand(BuiltinCommandInvoc):
    expected_command = "echo"

    def run_core(self):
        runner = Runner(self.spec(), self.shell_context())
        runner.start()
        return runner.future_shell_context()
