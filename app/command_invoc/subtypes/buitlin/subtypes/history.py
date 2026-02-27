
from app.command_invoc.models import NextLineShellContext
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc

from multiprocessing import Process
import os
import sys

from app.shell import add_history



    
    
class ShellContextUpdate:
    def __init__(self, value, is_update):
        self._value = value
        self._is_update = is_update

    @classmethod
    def no_update(cls):
        return cls(None, False)

    @classmethod
    def new(cls, value):
        return cls(value, True)

    def is_update(self):
        return self._is_update

    def value(self):
        return self._value

        
from abc import ABC, abstractmethod       
class InvocRunner(ABC):
    
    def __init__(self, spec, shell_context):
        self._spec = spec
        self._shell_context = shell_context
        self._updated_end_shell_context = ShellContextUpdate.no_update()
        
    @abstractmethod 
    def runny(self):
        pass
        
    
    def start(self):
        res = self.runny()
        if res != None:
            self._updated_end_shell_context = ShellContextUpdate.new( res )        
        
    def updated_end_shell_context(self):
        return self._updated_end_shell_context
    
class HistoryRunner(InvocRunner):
    
    def runny(self):        

        def history_line(line_num, line_content):
            return f"\t{line_num+1} {line_content}"

        def print_all_lines(history_lines):
            os.write( 1,  ("\n".join( history_lines ) + "\n").encode()  )

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

        history_lines = [ history_line(line_num, line) for line_num, line in enumerate( self._shell_context.history() ) ]

        if no_num_lines_arg():
            print_all_lines(history_lines)

        elif len( self._spec.args() ) == 1:
            print_last_n_lines( history_lines, num_lines_arg() )

        elif len( self._spec.args() ) == 2:
            
            read_flag = self._spec.args()[0]
            if read_flag != "-r":
                print("history: invalid arg " + read_flag, file=sys.stderr)
                
            else:
            
                read_res =  self._spec.args()[1]
                                
                with open(read_res, "r") as f:
                    lines = [ l.strip() for l in f.readlines()]
                    for line in lines:
                        if line:
                            add_history( self._shell_context, line  )    
        
        else:
            err_too_many_args() 
        
        return self._shell_context
        
        

class HistoryCommand(BuiltinCommandInvoc):

    expected_command = "history"

    def run_core(self):
        runner = HistoryRunner(self.spec(), self.shell_context())
        return runner
        
                   
        
        
                