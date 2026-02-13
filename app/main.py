from collections import namedtuple
import copy
from dataclasses import dataclass
import os 
import subprocess

import readline
import sys
from typing import List




    
class ExitCommand:
    
    def __init__(self, spec, end_pipe, shell_context):

        self._spec = spec
        self._shell_context = copy.deepcopy(shell_context)
        
    def spec(self):
        return self._spec
    
    def shell_context(self):
        return self._shell_context
    
    def run( self ):
        raise SystemExit(0)
    
class EchoCommand:
    
    def __init__(self, spec, end_pipe, shell_context):

        self._spec = spec
        self._shell_context = copy.deepcopy(shell_context)
        
    def spec(self):
        return self._spec
    
    def shell_context(self):
        return self._shell_context
    
    def run( self ):
        print( " ".join( self.spec().args() ) )
             

class TypeCommand:
    
    def __init__(self, spec, end_pipe, shell_context):

        self._spec = spec
        self._shell_context = copy.deepcopy(shell_context)
        
    def spec(self):
        return self._spec
    
    def shell_context(self):
        return self._shell_context

    def run(self):

        def _shell_builtin(arg):
            return arg in commands

        def _print_shell_builtin(arg):
            print(arg + " is a shell builtin")

        def _print_exec(arg, executable):
            print(arg + " is " + executable.full_path())

        def _err_not_found(arg):
            print(arg + ": not found")

        # ---- main loop ----
        for arg in self.spec().args():
            if _shell_builtin(arg):
                _print_shell_builtin(arg)
            else:
                executable = File.find_in_path(arg)
                if executable:
                    _print_exec(arg, executable)
                else:
                    _err_not_found(arg)

      
class PwdCommand:
    
    def __init__(self, spec, end_pipe, shell_context):

        self._spec = spec
        self._shell_context = copy.deepcopy(shell_context)
        
    def spec(self):
        return self._spec
    
    def shell_context(self):
        return self._shell_context

    def run(self):
        print( self.shell_context().cwd() )  
            
class CdCommand:
    
    def __init__(self, spec, end_pipe, shell_context):

        self._spec = spec
        self._shell_context = copy.deepcopy(shell_context)
        
    def spec(self):
        return self._spec
    
    def shell_context(self):
        return self._shell_context
    
    def run(self):
        
        def err_no_such_file_dir():
            print(f"cd: {target_path}: No such file or directory", file=sys.stderr) 
        
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
                return os.path.abspath(os.path.join(self.shell_context().cwd() , target_path))
            
            
        
        if( len(self.spec().args()) > 1 ):
            print("cd: too many arguments")
            
        target_path=self.spec().args()[0]
        target_full_path = absolute(target_path) 
            
        if os.path.isdir(target_full_path):
            self.shell_context().setcwd(target_full_path)
            
            
        else: 
            err_no_such_file_dir()
            
 
        
        
class HistoryCommand:
    
    def __init__(self, spec, end_pipe, shell_context):

        self._spec = spec
        self._shell_context = copy.deepcopy(shell_context)
        
    def spec(self):
        return self._spec
    
    def shell_context(self):
        return self._shell_context
    
    def run(self):
        
        def history_line(line_num, line_content):
            return f"\t{line_num+1} {line_content}"
         
        def print_all_lines(history_lines):
            print(   "\n".join( history_lines )   )
            
        def print_last_n_lines(history_lines, nl):
            print(   "\n".join( history_lines[-nl:] )   ) 
            
        def no_num_lines_arg():
            return len( self.spec().args() ) == 0
        
        def num_lines_arg():
            return int(self.spec().args()[0])
        
        def too_many_args():
            return len( self.spec().args() ) > 1
        
        def err_too_many_args():
            print("history: too many arguments", file=sys.stderr) 
        
        history_lines = [ history_line(line_num, line) for line_num, line in enumerate( self.shell_context().history() ) ] 
        
        if no_num_lines_arg():
            print_all_lines(history_lines)
            
        elif too_many_args():
            err_too_many_args()

        else:
            print_last_n_lines( history_lines, num_lines_arg() )
    
                
commands = {
    "exit" : ExitCommand,
    "echo" : EchoCommand,
    "type" : TypeCommand,
    "pwd" : PwdCommand,
    "cd" : CdCommand,
    "history"  : HistoryCommand
}

def is_builtin(command):
    return command in commands.keys()

def command_class(command):
    return commands[command] 



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
    
    
    # def command(line):
    #     return line.split()[0]
    
    # def args(line):
    #     return line.split()[1:]
    
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
    
    matching_commands = [ com for com in commands.keys() if com.startswith(text) ]  

    if multiple_matches_exist():
        return None
    
    matching_com = matching_commands[0]
    return matching_com


# Add iterators inside Line to loop through CommandInvocSpecs

# class Line:
#     def __init__( line ):
#         command_lines = line.split("|")
        


class CommandInvocSpec:
    
    def __init__( self, command_invoc_str ):
        self.command_invoc_str = command_invoc_str
    
    def __repr__(self):
        return self.command_invoc_str
    
    def command(self):
        return self.command_invoc_str.split()[0]
    
    def args(self):
        return self.command_invoc_str.split()[1:]
    


class CommandInvoc:
    def __init__( self, spec, end_pipe, shell_context ):
        self._spec = spec 
        self._end_pipe = end_pipe
        self._shell_context = copy.deepcopy(shell_context)
        
    def spec(self):
        return self._spec
       
    def end_pipe(self):
        return self._end_pipe
    
    def shell_context(self):
        return self._shell_context
    
    def setcwd(self, cwd):
        self._shell_context.setcwd(cwd)
       
    @classmethod 
    def resolve(cls, spec, end_pipe, shell_context):
        
        if is_builtin( spec.command() ):
            return BuiltinCommandInvoc(spec, end_pipe, shell_context)
        elif File.find_in_path( spec.command() ) :
            return ExecCommandInvoc(spec, end_pipe, shell_context)
        else:
            return NotFoundCommandInvoc(spec, end_pipe, shell_context)
  
  
        
class BuiltinCommandInvoc(CommandInvoc):
    # def run(self, shel)
    def run(self):
        CommandClass = command_class( self.spec().command() )
        
        com =  CommandClass ( self.spec(), self.end_pipe, self.shell_context())  # new command 
        com.run() #run command
        self.setcwd( com.shell_context().cwd() )




class ExecCommandInvoc(CommandInvoc):
    
    def run(self, stdin):
        # Start the process
        p = subprocess.Popen(
            [ self.spec().command() , *self.spec().args() ],
            stdin=stdin,
            stdout=sys.stdout if self.end_pipe() else subprocess.PIPE,
            stderr=sys.stderr,
            text=True,  # ensures input/output are str, not bytes
            cwd=self.shell_context().cwd()
        )
                                                
        if self.end_pipe():
            p.wait()

        return p.stdout

class NotFoundCommandInvoc (CommandInvoc):
    def run(self):
        return err_not_found(
            self.spec().command()
        )


        

#OK so a pipeline is when i have | in my command
# --> this works for now only for executable.
# so get com1 , com2. Make sure executables. 
# then run com2 with com1 as stdin

def main():
    
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)
    readline.set_auto_history(False)
    shell_context = ShellContext( os.getcwd(), [] )
    
    while True:
                
        command_lines = input_next_line()
        
        shell_context.set_history( shell_context.history() + ["|".join([str(cl) for cl in command_lines]) ]  )            
        
        command_invocs = [ CommandInvoc.resolve(command_invoc_spec, 
                                                  (index == len( command_lines ) - 1),
                                                  shell_context )
                          for index, command_invoc_spec in enumerate(command_lines) ]
        
        prev_stdout = subprocess.PIPE # This is the output pipe of previous command(process)
                                    
        # loop throught command lines
        for command_invoc in command_invocs:
            
            if isinstance(command_invoc, BuiltinCommandInvoc):
            
                if len(command_lines) != 1:
                    raise Exception("No pipes here yet!")
                
                command_invoc.run()
                
            elif isinstance(command_invoc, ExecCommandInvoc):
                prev_stdout = command_invoc.run( prev_stdout )
                
            elif isinstance( command_invoc, NotFoundCommandInvoc ):
                
                if len(command_lines) != 1:
                    raise Exception("No pipes here yet!")
                
                command_invoc.run()
                
            if command_invoc.end_pipe():
                shell_context.setcwd( command_invoc.shell_context().cwd() ) # set cwd
                                
            
                
if __name__ == "__main__":
    main()