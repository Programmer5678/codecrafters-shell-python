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
            
       
def gulag(line):
    sp0 = line.split("1>")
    sp1 = sp0[0].split(">")
    sp2 = sp0[1:]
    sp = sp1 + sp2
    
    liney = sp[0]
    redirect_to_last = None
    if len(sp) == 2:
        redirect_to_last = sp[1].strip()
        
    return liney , redirect_to_last
            
def invocs(line, shell_context):
    
    liney, redirect_to_last = gulag(line)
    
    raw_invocs = liney.split("|")
    result = []
    
    for index, raw_invoc in enumerate( raw_invocs ):
        
        
        def create_invoc(raw_invoc, in_pipe, end_pipe, shell_context, redirect_to):
            return CommandInvoc.resolve_subclass(
                                        CommandInvocArgs(
                                            CommandInvocSpec( raw_invoc ), 
                                            in_pipe,
                                            end_pipe,
                                            shell_context,
                                            redirect_to
                                        )
                        )
            
        in_pipe = len( raw_invocs) > 1
        end_pipe = (index == len( raw_invocs ) - 1)
        redirect_to = redirect_to_last if end_pipe else None
        result.append(create_invoc(raw_invoc, in_pipe, end_pipe, shell_context, redirect_to))
        
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
            
        if command_invoc.end_pipe():
            result.end_cwd = command_invoc.shell_context().cwd() 
            
        return result
            
        
         
    
    
    
            
def main():
    
    setup_interactive_shell()
    shell_context = ShellContext( os.getcwd() )
    
    for line in input_lines():
        
        
        shell_context.add_line_history(line)
        command_invocs = invocs(line, shell_context)
                
        state = CommandInvocIter()                            
        for command_invoc in command_invocs:
            state = state.next_state(command_invoc)
                            
        state.proc_waiter.wait_for_all()
        if state.end_cwd:
            shell_context.setcwd( state.end_cwd )                             
            
                
if __name__ == "__main__":
    main()