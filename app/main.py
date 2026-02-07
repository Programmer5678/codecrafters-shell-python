import sys
import os 

from abc import ABC, abstractmethod
import subprocess

class Command(ABC):
    
    def __init__(self, args):
        self._args = args
        
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
        print( os.getcwd() )      
             
                
commands = {
    "exit" : ExitCommand,
    "echo" : EchoCommand,
    "type" : TypeCommand,
    "pwd" : PwdCommand
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
    
    
    
    
    
    
    
    

    
def main():
    
    def print_not_found(command):
        print(f"{command}: command not found")    
        
    def input_next_line():
        print("$ ", end="", flush=True)
        line = sys.stdin.readline()
        
        def command(line):
            return line.split()[0]
        
        def args(line):
            return line.split()[1:]
        
        return { "command" : command(line), "args": args(line)}
        
        
    
    while True:
                
        next_line = input_next_line()
        next_command = next_line["command"]
                
        if next_command in commands.keys(): 
            commands[next_command](next_line["args"]).run() 
            
        elif File.find_in_path(next_command) :
            subprocess.run(
                [next_command, *next_line["args"]]
            )         
                           
        else:
            print_not_found( next_command )
                  
  
            

if __name__ == "__main__":
    main()
