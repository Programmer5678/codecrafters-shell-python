from app.command_invoc.models import FutureShellContext
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from app.search_files import find_in_path

from multiprocessing import Process
import os


def runny(spec, shell_context):

    def _print_shell_builtin(com):
        os.write(1, (com + " is a shell builtin\n").encode())

    def _print_exec(com, executable):
        os.write(1, (com + " is " + executable.full_path() + "\n").encode())

    def _err_not_found(com):
        os.write(1, (com + ": not found\n").encode())

    for arg in spec.args():
        if BuiltinCommandInvoc.is_builtin(arg):
            _print_shell_builtin(arg)
        else:
            executable = find_in_path(arg)
            if executable:
                _print_exec(arg, executable)
            else:
                _err_not_found(arg)

    return FutureShellContext.keep_previous()


class Runner:
    
    def __init__(self, spec, shell_context):
        self._spec = spec
        self._shell_context = shell_context
        self._future_shell_context = None
        
    def start(self):
        self._future_shell_context = runny(self._spec, self._shell_context)
        
    def future_shell_context(self):
        return self._future_shell_context


class TypeCommand(BuiltinCommandInvoc):
    expected_command = "type"

    def run_core(self):
        runner = Runner(self.spec(), self.shell_context())
        return runner


