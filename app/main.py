import copy
import os 
import readline
import subprocess

import sys
from typing import List

from app.command_invoc.models import PipelineResult
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from app.command_invoc.subtypes.exec import ExecCommandInvoc
from app.command_invoc.subtypes.notfound import NotFoundCommandInvoc
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from app.command_invoc.subtypes.buitlin.subtypes.cd import CdCommand
from app.command_invoc.subtypes.buitlin.subtypes.echo import EchoCommand
from app.command_invoc.subtypes.buitlin.subtypes.exit import ExitCommand
from app.command_invoc.subtypes.buitlin.subtypes.history import HistoryCommand
from app.command_invoc.subtypes.buitlin.subtypes.pwd import PwdCommand
from app.command_invoc.subtypes.buitlin.subtypes.type import TypeCommand

from app.command_line import input_lines
from app.interactive_shell import setup_interactive_shell


class ShellContext:
    
    def __init__(self, cwd):
        self._cwd = cwd
        self._history = []
        
    def cwd(self):
        return self._cwd
    
    def history(self):
        return self._history
    
    def setcwd(self, cwd):
        self._cwd = cwd

    def add_line_history(self, line):
        self._history.append(line)




class ProcWaiter:
    def __init__(self):
        self._waiter_funcs = []
        
    def add_waiter(self, waiter):
        self._waiter_funcs.append(waiter)
        
    def wait_for_all(self):
        
        for waiter in self._waiter_funcs:
            waiter()
            
     
class CommandInvocIter:
    
    def __init__(self):
        STDIN = 0
        
        self.next_stdin = STDIN
        self.proc_waiter = ProcWaiter()
        self.end_cwd = None
        
        
    def next_state(self, command_invoc):
        
        result = copy.deepcopy(self)
        
        pipeline_res = command_invoc.run(result.next_stdin)
        result.next_stdin = pipeline_res.next_stdin()
        result.proc_waiter.add_waiter(  pipeline_res.wait_child_end() ) 
            
        if command_invoc.last_invoc():
            result.end_cwd = command_invoc.shell_context().cwd() 
            
        return result
            
            
def main():
    
    setup_interactive_shell()
    shell_context = ShellContext( os.getcwd() )
    
    for line in input_lines():
                
        shell_context.add_line_history(line.raw )
        readline.add_history( line.raw )
                
        state = CommandInvocIter()                            
        for command_invoc in line.invocs(shell_context):
            state = state.next_state(command_invoc)
                            
        state.proc_waiter.wait_for_all()
        if state.end_cwd:
            shell_context.setcwd( state.end_cwd )                             
            
                
if __name__ == "__main__":
    main()