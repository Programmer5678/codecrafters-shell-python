from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from app.search_files import find_in_path

from multiprocessing import Process
import os


class TypeCommand(BuiltinCommandInvoc):

    expected_command="type"

    def run_core(self ):

        def _print_shell_builtin(com):
            os.write( 1, (com + " is a shell builtin"+ "\n").encode() )

        def _print_exec(com, executable):
            os.write( 1, (com + " is " + executable.full_path() + "\n").encode() )

        def _err_not_found(com):
            os.write( 1,  (com + ": not found" + "\n").encode() )

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
                    
    
