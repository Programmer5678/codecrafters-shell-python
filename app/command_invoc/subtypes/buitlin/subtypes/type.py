from app.command_invoc.models import NextLineShellContext
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


class TypeCommand(BuiltinCommandInvoc):
    expected_command = "type"

    def run_core(self):
        runner = Runner(self.spec(), self.shell_context())
        return runner


