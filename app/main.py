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









class File:
    
    def __init__ (self, dir_path, file):
        self._dir_path = dir_path
        self._file = file
        
    def file(self):
        return self._file
    
    def dir_path(self):
        return self._dir_path
    
    def full_path(self):
        return os.path.join(self.dir_path(), self.file())
    

    @classmethod
    def _all_dirs(cls, dir_paths ):
        return [   dir_path for dir_path in dir_paths if os.path.isdir( dir_path )   ]
        
    @classmethod
    def _all_files(cls, dir_paths):
        
        result = []
        
        for dir_path in File._all_dirs(dir_paths):
            for file_name in os.listdir(dir_path):
                
                file = File( dir_path, file_name)
                
                if os.path.isfile( file.full_path() ):
                        
                    result.append(file)
                    
        return result
    
    @classmethod
    def find_exec(cls, dir_paths, looking_for):
                
        for file in File._all_files(dir_paths):
            if looking_for == file.file() and os.access( file.full_path(), os.X_OK):
                return file
                
        return None
        

    @classmethod
    def find_in_path(cls, arg):
        
        def path_dirs():
            return os.environ.get("PATH").split(":")
        
        return File.find_exec(path_dirs(), arg)
    
    


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



# [ { "command" : command(com), "args": args(com)} for com in com_lines ]
                
def err_not_found(command):
    print(f"{command}: command not found", file=sys.stderr)     


    
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
                                
            
                
if __name__ == "__main__":
    main()