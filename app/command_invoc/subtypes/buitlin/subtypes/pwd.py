from app.command_invoc.models import NextLineShellContext
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc

from multiprocessing import Process
import os
from app.command_invoc.invoc_runner import InvocRunner


class PwdRunner(InvocRunner):
    def run(self):
        os.write(1, (self._shell_context.cwd() + "\n").encode())
        
class PwdCommand(BuiltinCommandInvoc):
    expected_command = "pwd"

    def run_core(self):
        runner = PwdRunner(self.spec(), self.shell_context())
        return runner
