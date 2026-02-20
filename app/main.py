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
            
            
def invocs(line, shell_context):
    
    raw_invocs = line.split("|")
    result = []
    
    for index, raw_invoc in enumerate( raw_invocs ):
        
        
        def create_invoc(raw_invoc, in_pipe, end_pipe, shell_context):
            return CommandInvoc.resolve_subclass(
                                        CommandInvocArgs(
                                            CommandInvocSpec( raw_invoc ), 
                                            in_pipe,
                                            end_pipe,
                                            shell_context
                                        )
                        )
            
        in_pipe = len( raw_invocs) > 1
        end_pipe = index == len( raw_invocs ) - 1
        result.append(create_invoc(raw_invoc, in_pipe, end_pipe, shell_context))
        
    return result
            
            
def main():
    
    setup_interactive_shell()
    shell_context = ShellContext( os.getcwd() )
    
    for line in input_lines():
        
        shell_context.add_line_history(line)
        command_invocs = invocs(line, shell_context)
        
        STDIN = 0
        next_stdin = STDIN        
        proc_waiter = ProcWaiter()
        apply_line_effect = lambda : None
                                    
        # loop throught command lines
        for command_invoc in command_invocs:
                            
            pipeline_res = command_invoc.run(next_stdin)
            next_stdin = pipeline_res.next_stdin()
            proc_waiter.add_waiter(  pipeline_res.wait_child_end() ) 
                
               
            if command_invoc.end_pipe():
                set_shell_cwd = lambda : shell_context.setcwd( command_invoc.shell_context().cwd() )
                apply_line_effect = set_shell_cwd 
    
        proc_waiter.wait_for_all()
        apply_line_effect()                                
            
                
if __name__ == "__main__":
    main()