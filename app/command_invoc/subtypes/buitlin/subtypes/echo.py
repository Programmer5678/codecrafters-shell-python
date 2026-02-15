from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from multiprocessing import Process
import os


class EchoCommand(BuiltinCommandInvoc):

    expected_command="echo"

    def run( self, stdin ):
        
        if self.end_pipe():
            next_stdin = None
            p = Process(target=self.on_way, args=( 1 ,))
            p.start()
            
        else:
            next_stdin, stdout = os.pipe()
            # os.write(stdout, b"hi")
            
            print( "A Proc: ", os.getpid() , " parent : ", os.getppid() )
            print( "Fd stat :", os.fstat(stdout) )
            
            p = Process(target=self.on_way, args=(stdout,))
            p.start()
            os.close(stdout)
        
        if stdin:
            os.close(stdin)
        
        return next_stdin, lambda : p.join()
    
    def on_way(self, out):
        
        self.actual_run(out)
        if out != 1: # 1 = STDOUT
            pass
            os.close( out )
    
    def actual_run(self, out):
        
        print( "Proc: ", os.getpid() , " parent : ", os.getppid() )
        print( "Fd stat :", os.fstat(out) )
        os.write( out, (" ".join( self.spec().args()) + "\n").encode() )
        