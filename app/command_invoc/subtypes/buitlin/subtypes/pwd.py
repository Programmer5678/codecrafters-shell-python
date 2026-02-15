from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc

from multiprocessing import Process
import os

class PwdCommand(BuiltinCommandInvoc):

    expected_command="pwd"

    def actual_run(self, out):
        os.write( out, (self.shell_context().cwd()+"\n").encode() )
        
    def run( self, stdin ):
        
        if self.end_pipe():
            next_stdin = None
            p = Process(target=self.on_way, args=( 1 ,))
            p.start()
            
        else:
            next_stdin, stdout = os.pipe()
            p = Process(target=self.on_way, args=(stdout,))
            p.start()
            os.close(stdout)
        
        if stdin:
            os.close(stdin)
        
        return next_stdin, lambda : p.join()

    def on_way(self, out):
        
        self.actual_run(out)
        if out != 1: # 1 = STDOUT
            os.close( out )