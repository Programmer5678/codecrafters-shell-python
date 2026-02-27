from app.command_invoc.invoc_runner import InvocRunner
from app.command_invoc.models import NextLineShellContext
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from multiprocessing import Process
import os


class EchoRunner(InvocRunner):
    
    def run(self):
        os.write(1, (" ".join(self._spec.args()) + "\n").encode())


class EchoCommand(BuiltinCommandInvoc):
    expected_command = "echo"

    def run_core(self):
        runner = EchoRunner(self.spec(), self.shell_context())
        return runner
