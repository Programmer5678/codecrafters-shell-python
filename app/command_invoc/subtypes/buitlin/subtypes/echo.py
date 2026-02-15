from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from multiprocessing import Process
import os


class EchoCommand(BuiltinCommandInvoc):

    expected_command="echo"

    def run( self, stdin ):
        
                
        if self.end_pipe():
            next_stdin = None
            
            child_pid = os.fork()
            if child_pid == 0:
                self.on_way(1)
                os._exit(0)
            
        else:
            next_stdin, stdout = os.pipe()
                  
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
    
    def on_way(self, out):
        
        self.actual_run(out)
        if out != 1: # 1 = STDOUT
            pass
            os.close( out )
    
    def actual_run(self, out):
        
        os.write( out, (" ".join( self.spec().args()) + "\n").encode() )
        