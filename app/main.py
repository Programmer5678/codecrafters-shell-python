import copy
import os 
import subprocess

import readline
import sys
from typing import List

from app.command_invoc.models import CommandInvoc, PipelineResult
from app.command_invoc.models import CommandInvocArgs
from app.command_invoc.models import CommandInvocSpec
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

def input_next_line():
        
    def empty_line(line):
        return line == None or len(line.split()) == 0
    
    line = None
    while empty_line(line):
        line = input("$ ")
    
    readline.add_history(line)
    
    return line

def input_lines():
    while True:
        yield input_next_line()




class ProcWaiter:
    def __init__(self):
        self._waiter_funcs = []
        
    def add_waiter(self, waiter):
        self._waiter_funcs.append(waiter)
        
    def wait_for_all(self):
        
        for waiter in self._waiter_funcs:
            waiter()
            
     
class Line:
    
    def __init__(self, raw):
        self.raw = raw
        
    def split_redirect(self):
        def split_on(st, split_a, split_b):
            st_first_split = st.split(split_a)
            resplit_start = st_first_split[0].split(split_b)
            return resplit_start + st_first_split[1:]
            
        
        return split_on(self.raw, "1>", ">")
    
    def invocs_part(self):
        return self.split_redirect()[0]
    
    def redirect_part(self):
        
        split_red = self.split_redirect()
        
        if len(split_red) == 2:
            return split_red[1].strip()
            
        return None
        
       
            
def invocs(line_obj, shell_context):
    
    
    raw_invocs = line_obj.invocs_part().split("|")
    result = []
    
    for index, raw_invoc in enumerate( raw_invocs ):
        
        
        def create_invoc(raw_invoc, in_pipe, last_invoc, shell_context, redirect_to):
            return CommandInvoc.resolve_subclass(
                                        CommandInvocArgs(
                                            CommandInvocSpec( raw_invoc ), 
                                            in_pipe,
                                            last_invoc,
                                            shell_context,
                                            redirect_to
                                        )
                        )
            
        in_pipe = len( raw_invocs) > 1
        last_invoc = (index == len( raw_invocs ) - 1)
        redirect_to = line_obj.redirect_part() if last_invoc else None # If not last invoc, we dont redirect the stdout anywhere
        result.append(create_invoc(raw_invoc, in_pipe, last_invoc, shell_context, redirect_to))
        
    return result
            
            
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
        
        line_obj = Line(line)
        
        shell_context.add_line_history(line)
        command_invocs = invocs(line_obj, shell_context)
                
        state = CommandInvocIter()                            
        for command_invoc in command_invocs:
            state = state.next_state(command_invoc)
                            
        state.proc_waiter.wait_for_all()
        if state.end_cwd:
            shell_context.setcwd( state.end_cwd )                             
            
                
if __name__ == "__main__":
    main()