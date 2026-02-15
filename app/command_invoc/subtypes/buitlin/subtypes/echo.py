from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from multiprocessing import Process
import os


class EchoCommand(BuiltinCommandInvoc):

    expected_command="echo"

    def run( self, stdin ):
        
        next_stdin, stdout = ( None, 1 ) if self.end_pipe() else os.pipe()
                
                
        child_pid = os.fork()   
        if child_pid == 0:
            self.actual_run(stdout)
            if stdout != 1:
                os.close(stdout)
            os._exit(0)
        
        
        if stdout != 1: 
            os.close(stdout)
        
        if stdin:
            os.close(stdin)
        
        return next_stdin, lambda : os.waitpid( child_pid , 0)
    
    
    def actual_run(self, out):
        
        os.write( out, (" ".join( self.spec().args()) + "\n").encode() )
        