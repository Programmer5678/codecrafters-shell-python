
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
import os
import sys
from app.shell import add_history
from app.command_invoc.invoc_runner import InvocRunner

    
class HistoryRunner(InvocRunner):
    
    def run(self):        

        def history_line(line_num, line_content):
            return f"\t{line_num+1} {line_content}"

        def print_all_lines(history_lines):
            print ( "\n".join( history_lines ) + "\n" , end="")

        def print_last_n_lines(history_lines, nl):
            os.write( 1,  ("\n".join( history_lines[-nl:] ) + "\n").encode()   )

        def no_num_lines_arg():
            return len( self._spec.args() ) == 0

        def num_lines_arg():
            return int( self._spec.args()[0])

        def too_many_args():
            return len( self._spec.args() ) > 1

        def err_too_many_args():
            print("history: too many arguments", file=sys.stderr)
            
        def lines_to_file(file):
            lines = self._shell_context.history()
            print( "\n".join( lines ), file=file )

        history_lines = [ history_line(line_num, line) for line_num, line in enumerate( self._shell_context.history() ) ]
        
        if no_num_lines_arg():
            print_all_lines(history_lines)

        elif len( self._spec.args() ) == 1:
            print_last_n_lines( history_lines, num_lines_arg() )

        elif len( self._spec.args() ) == 2:
            
            flag = self._spec.args()[0]
            if flag == "-r":
                read_res =  self._spec.args()[1]
                                
                with open(read_res, "r") as f:
                    lines = [ l.strip() for l in f.readlines()]
                    for line in lines:
                        if line:
                            add_history( self._shell_context, line  )
                            
            elif flag == "-w":
                
                def absolute(target_path):

                    def is_absolute(path):
                        return path[0] == '/'

                    def is_home_dir(path):
                        return path == "~"

                    def home_dir():
                        return os.path.expanduser("~")

                    if is_absolute(target_path):
                        return os.path.abspath(target_path)

                    elif is_home_dir(target_path):
                        return home_dir()

                    else:
                        return os.path.abspath(os.path.join(self._shell_context.cwd() , target_path))

                write_to = absolute( self._spec.args()[1]  )
                with open(write_to, "w") as f:
                    lines_to_file( f )

            else:
                print("history: invalid arg " + flag, file=sys.stderr)
                
        
        else:
            err_too_many_args() 
        
        return self._shell_context
        
        

class HistoryCommand(BuiltinCommandInvoc):

    expected_command = "history"

    def run_core(self):
        runner = HistoryRunner(self.spec(), self.shell_context())
        return runner
        
                   
        
        
                