from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
import os


def runny(spec, shell_context):
    os._exit(0)

class Runner:
    
    def __init__(self, spec, shell_context):
        self._spec = spec
        self._shell_context = shell_context
        self._future_shell_context = None
        
    def start(self):
        self._future_shell_context = runny(self._spec, self._shell_context)
        
    def future_shell_context(self):
        return self._future_shell_context

class ExitCommand(BuiltinCommandInvoc):
    expected_command = "exit"

    def run_core(self):
        runner = Runner(self.spec(), self.shell_context())
        runner.start()
        return runner.future_shell_context()
