import os 
import subprocess

import readline
import sys
from typing import List

from app.command_invoc.models import CommandInvoc
from app.command_invoc.models import CommandInvocArgs
from app.command_invoc.models import CommandInvocSpec
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from app.command_invoc.subtypes.exec import ExecCommandInvoc
from app.command_invoc.subtypes.notfound import NotFoundCommandInvoc

from app.command_invoc.subtypes.buitlin.subtypes.cd import CdCommand
from app.command_invoc.subtypes.buitlin.subtypes.echo import EchoCommand
from app.command_invoc.subtypes.buitlin.subtypes.exit import ExitCommand
from app.command_invoc.subtypes.buitlin.subtypes.history import HistoryCommand
from app.command_invoc.subtypes.buitlin.subtypes.pwd import PwdCommand
from app.command_invoc.subtypes.buitlin.subtypes.type import TypeCommand


class ShellContext:
    
    def __init__(self, cwd, history):
        self._cwd = cwd
        self._history = history
        
    def cwd(self):
        return self._cwd
    
    def history(self):
        return self._history
    
    def setcwd(self, cwd):
        self._cwd = cwd
            
    def set_history(self, history):
        self._history = history


def input_next_line():
        
    def empty_line(line):
        return line == None or len(line.split()) == 0
    
    line = None
    while empty_line(line):
        line = input("$ ")
    
    readline.add_history(line)
    
    com_lines = line.split("|")
    

    return [ CommandInvocSpec(com_line ) for  com_line in com_lines ]


    
def completer(text: str, state: int) -> str:
    
    def not_first_match():
        return state > 0
    
    def multiple_matches_exist():
        return len(matching_commands) > 1
    
    if not_first_match():
        return None
    
    matching_commands = [ com for com in BuiltinCommandInvoc.commands().keys() if com.startswith(text) ]  

    if multiple_matches_exist():
        return None
    
    matching_com = matching_commands[0]
    return matching_com


def main():
    
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)
    readline.set_auto_history(False)
    shell_context = ShellContext( os.getcwd(), [] )
    
    while True:
                
        command_lines = input_next_line()
        
        shell_context.set_history( shell_context.history() + ["|".join([str(cl) for cl in command_lines]) ]  )            
        
        command_invocs = [ CommandInvoc.resolve(
                                            CommandInvocArgs(
                                            command_invoc_spec, 
                                                len(command_lines) > 1,# in pipe
                                                  (index == len( command_lines ) - 1),
                                                  shell_context
                                            )
                            )
                          for index, command_invoc_spec in enumerate(command_lines) ]
        
        prev_stdout = subprocess.PIPE # This is the output pipe of previous command(process)
                                    
        # loop throught command lines
        for command_invoc in command_invocs:
            
            if isinstance(command_invoc, BuiltinCommandInvoc):
            
                if len(command_lines) != 1:
                    raise Exception("No pipes here yet!")
                
                command_invoc.run(None)
                
            elif isinstance(command_invoc, ExecCommandInvoc):
                prev_stdout = command_invoc.run( prev_stdout )
                
            elif isinstance( command_invoc, NotFoundCommandInvoc ):
                
                if len(command_lines) != 1:
                    raise Exception("No pipes here yet!")
                
                command_invoc.run(None)
                
            if command_invoc.end_pipe():
                shell_context.setcwd( command_invoc.shell_context().cwd() ) # set cwd
                print("SHOULD BE DONE")
                                
            
                
if __name__ == "__main__":
    main()