from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc

from multiprocessing import Process
import os

class PwdCommand(BuiltinCommandInvoc):

    expected_command="pwd"

    def run_core(self, out):
        os.write( out, (self.shell_context().cwd()+"\n").encode() )
        