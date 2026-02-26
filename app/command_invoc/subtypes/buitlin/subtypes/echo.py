from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from multiprocessing import Process
import os


def runny(spec, shell_context):
    os.write(1, (" ".join(spec.args()) + "\n").encode())
    return shell_context


class EchoCommand(BuiltinCommandInvoc):
    expected_command = "echo"

    def run_core(self):
        return runny(self.spec(), self.shell_context())
