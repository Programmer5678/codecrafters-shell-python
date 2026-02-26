from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc

from multiprocessing import Process
import os

def runny(spec, shell_context):
    os.write(1, (shell_context.cwd() + "\n").encode())
    return shell_context


class PwdCommand(BuiltinCommandInvoc):
    expected_command = "pwd"

    def run_core(self):
        return runny(self.spec(), self.shell_context())
