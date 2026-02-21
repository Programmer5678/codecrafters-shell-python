from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from multiprocessing import Process
import os


class EchoCommand(BuiltinCommandInvoc):

    expected_command="echo"
    
    def run_core(self):
        
        os.write( 1, (" ".join( self.spec().args()) + "\n").encode() )
        