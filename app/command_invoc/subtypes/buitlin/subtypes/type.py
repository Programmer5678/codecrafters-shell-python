from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from app.search_files import find_in_path

from multiprocessing import Process
import os


class TypeCommand(BuiltinCommandInvoc):

    expected_command="type"

    def actual_run(self, out ):

        def _print_shell_builtin(com):
            os.write( out, (com + " is a shell builtin"+ "\n").encode() )

        def _print_exec(com, executable):
            os.write( out, (com + " is " + executable.full_path() + "\n").encode() )

        def _err_not_found(com):
            os.write( out,  (com + ": not found" + "\n").encode() )

        # ---- main loop ----
        for arg in self.spec().args():
            if BuiltinCommandInvoc.is_builtin(arg):
                _print_shell_builtin(arg)
            else:
                executable = find_in_path(arg)
                if executable:
                    _print_exec(arg, executable)
                else:
                    _err_not_found(arg)
                    
    
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