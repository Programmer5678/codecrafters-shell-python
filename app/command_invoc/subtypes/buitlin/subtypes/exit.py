from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
import sys
from app.command_invoc.invoc_runner import InvocRunner



class ExitRunner(InvocRunner):
    def run(self):
        sys.exit()
        

class ExitCommand(BuiltinCommandInvoc):
    expected_command = "exit"

    def run_core(self):
        runner = ExitRunner(self.spec(), self.shell_context())
        return runner
