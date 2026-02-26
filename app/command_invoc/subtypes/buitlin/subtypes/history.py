
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc

from multiprocessing import Process
import os
import sys

from app.shell import add_history


def runny(spec, shell_context):        

    def history_line(line_num, line_content):
        return f"\t{line_num+1} {line_content}"

    def print_all_lines(history_lines):
        os.write( 1,  ("\n".join( history_lines ) + "\n").encode()  )

    def print_last_n_lines(history_lines, nl):
        os.write( 1,  ("\n".join( history_lines[-nl:] ) + "\n").encode()   )

    def no_num_lines_arg():
        return len( spec.args() ) == 0

    def num_lines_arg():
        return int(spec.args()[0])

    def too_many_args():
        return len( spec.args() ) > 1

    def err_too_many_args():
        print("history: too many arguments", file=sys.stderr)

    history_lines = [ history_line(line_num, line) for line_num, line in enumerate( shell_context.history() ) ]

    if no_num_lines_arg():
        print_all_lines(history_lines)

    elif len( spec.args() ) == 1:
        print_last_n_lines( history_lines, num_lines_arg() )

    elif len( spec.args() ) == 2:
        
        read_flag = spec.args()[0]
        if read_flag != "-r":
            print("history: invalid arg " + read_flag, file=sys.stderr)
            
        else:
        
            read_res =  spec.args()[1]
                            
            with open(read_res, "r") as f:
                lines = [ l.strip() for l in f.readlines()]
                for line in lines:
                    if line:
                        add_history( shell_context, line  )    
    
    else:
        err_too_many_args() 
        
        
    
    return shell_context
    
    
class Runner:
    
    def __init__(self, spec, shell_context):
        self._spec = spec
        self._shell_context = shell_context
        self._future_shell_context = None
        
    def start(self):
        self._future_shell_context = runny(self._spec, self._shell_context)
        
    def future_shell_context(self):
        return self._future_shell_context    

class HistoryCommand(BuiltinCommandInvoc):

    expected_command = "history"

    def run_core(self):
        runner = Runner(self.spec(), self.shell_context())
        runner.start()
        return runner.future_shell_context()
        
                   
        
        
                