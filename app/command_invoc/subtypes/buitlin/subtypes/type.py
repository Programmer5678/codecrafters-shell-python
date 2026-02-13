from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from app.main import File


class TypeCommand(BuiltinCommandInvoc):

    expected_command="type"

    def run(self, stdin):

        def _print_shell_builtin(com):
            print(com + " is a shell builtin")

        def _print_exec(com, executable):
            print(com + " is " + executable.full_path())

        def _err_not_found(com):
            print(com + ": not found")

        # ---- main loop ----
        for arg in self.spec().args():
            if BuiltinCommandInvoc.is_builtin(arg):
                _print_shell_builtin(arg)
            else:
                executable = File.find_in_path(arg)
                if executable:
                    _print_exec(arg, executable)
                else:
                    _err_not_found(arg)