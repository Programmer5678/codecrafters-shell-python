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