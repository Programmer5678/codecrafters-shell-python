from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from app.search_files import find_in_path
from app.command_invoc.invoc_runner import InvocRunner
import os



class TypeRunner(InvocRunner):
    def run(self):

        def _print_shell_builtin(com):
            os.write(1, (com + " is a shell builtin\n").encode())

        def _print_exec(com, executable):
            os.write(1, (com + " is " + executable.full_path() + "\n").encode())

        def _err_not_found(com):
            os.write(1, (com + ": not found\n").encode())

        for arg in self._spec.args():
            if BuiltinCommandInvoc.is_builtin(arg):
                _print_shell_builtin(arg)
            else:
                executable = find_in_path(arg)
                if executable:
                    _print_exec(arg, executable)
                else:
                    _err_not_found(arg)

class TypeCommand(BuiltinCommandInvoc):
    expected_command = "type"

    def run_core(self):
        runner = TypeRunner(self.spec(), self.shell_context())
        return runner


