import os 
from abc import ABC, abstractmethod
import subprocess

import readline


class Command(ABC):
    
    def __init__(self, args, shell_context):
        self._args = args
        self.shell_context = shell_context
        
    def args(self):
        return self._args
    
    @abstractmethod
    def run( self ):
        pass
    
class ExitCommand(Command):
    def run( self ):
        raise SystemExit(0)
    
class EchoCommand(Command):
    def run( self ):
        print( " ".join( self.args() ) )
             

class TypeCommand(Command):

    def run(self):

        def _shell_builtin(arg):
            return arg in commands

        def _print_shell_builtin(arg):
            print(arg + " is a shell builtin")

        def _print_exec(arg, executable):
            print(arg + " is " + executable.full_path())

        def _print_not_found(arg):
            print(arg + ": not found")

        # ---- main loop ----
        for arg in self.args():
            if _shell_builtin(arg):
                _print_shell_builtin(arg)
            else:
                executable = File.find_in_path(arg)
                if executable:
                    _print_exec(arg, executable)
                else:
                    _print_not_found(arg)

      
class PwdCommand(Command):

    def run(self):
        print( self.shell_context.cwd() )  
            
class CdCommand(Command):
    
    def run(self):
        
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
                return os.path.abspath(os.path.join(self.shell_context.cwd() , target_path))
            
            
        
        if( len(self.args()) > 1 ):
            print("cd: too many arguments")
            
        target_path=self.args()[0]
        target_full_path = absolute(target_path) 
            
        if os.path.isdir(target_full_path):
            self.shell_context.setcwd(target_full_path)
            
            
        else: 
            print(f"cd: {target_path}: No such file or directory")    
            
            
        
        
class HistoryCommand(Command):
    
    def run(self):
        
        def history_line(line_num, line_content):
            return f"\t{line_num+1} {line_content}"
         
        def print_all_lines(history_lines):
            print(   "\n".join( history_lines )   )
            
        def print_last_n_lines(history_lines, nl):
            print(   "\n".join( history_lines[-nl:] )   ) 
            
        def no_num_lines_arg():
            return len( self.args() ) == 0
        
        def num_lines_arg():
            return int(self.args()[0])
        
        def too_many_args():
            return len( self.args() ) > 1
        
        def print_too_many_args():
            print("history: too many arguments") 
        
        history_lines = [ history_line(line_num, line) for line_num, line in enumerate( self.shell_context.history() ) ] 
        
        if no_num_lines_arg():
            print_all_lines(history_lines)
            
        elif too_many_args():
            print_too_many_args()

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






def input_next_line(add_history):
        
    def empty_line(line):
        return line == None or len(line.split()) == 0
    
    def command(line):
        return line.split()[0]
    
    def args(line):
        return line.split()[1:]
    
    line = None
    while empty_line(line):
        line = input("$ ")
    
    add_history(line)
        
    return { "command" : command(line), "args": args(line)}
                
def print_not_found(command):
    print(f"{command}: command not found")   
    

def add_line( history, next_line ):
    return history + [ next_line["command"] + " " + " ".join(next_line["args"]) ]
    

    
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

    
def readline_setup():
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)
    readline.set_auto_history(False)
    
def main():
    
    shell_context = ShellContext( os.getcwd(), [] )
    
    while True:
                
        next_line = input_next_line(readline.add_history)
        shell_context.set_history( add_line( shell_context.history(), next_line ) )
        
        next_command = next_line["command"]
        
        if next_command in commands.keys(): 
            CommandClass = commands[next_command]
            com =  CommandClass ( next_line["args"], shell_context )
            com.run()
            shell_context.setcwd( com.shell_context.cwd() )
        
        elif File.find_in_path(next_command) :
            subprocess.run(
                [next_command, *next_line["args"]],
                cwd=shell_context.cwd()
            )         
                           
        else:
            print_not_found( next_command )
                  


if __name__ == "__main__":
    main()