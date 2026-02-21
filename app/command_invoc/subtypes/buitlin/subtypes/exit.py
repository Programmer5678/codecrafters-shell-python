from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
import os

class ExitCommand(BuiltinCommandInvoc):

    expected_command = "exit"
        
    def run_core(self):
        os._exit(0)
        