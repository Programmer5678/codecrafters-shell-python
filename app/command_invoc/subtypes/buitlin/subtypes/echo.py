from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from multiprocessing import Process
import os


class EchoCommand(BuiltinCommandInvoc):

    expected_command="echo"
    
    def run_core(self, out):
        
        os.write( out, (" ".join( self.spec().args()) + "\n").encode() )
        