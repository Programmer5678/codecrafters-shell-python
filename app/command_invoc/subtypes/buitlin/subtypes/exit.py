from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
import os


def runny(spec, shell_context):
    os._exit(0)


class ExitCommand(BuiltinCommandInvoc):
    expected_command = "exit"

    def run_core(self):
        return runny(self.spec(), self.shell_context())
