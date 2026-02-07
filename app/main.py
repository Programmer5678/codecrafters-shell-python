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
        
        for arg in self.args():
            if self._shell_builtin(arg):
                self._print_shell_builtin(arg)
            else:
                executable = self._search_in_path(arg)
                if executable:
                    self._print_exec(arg, executable)
                else:
                    self._print_not_found(arg)

    # ---- helpers ----

    def _get_path_dirs(self):
        return os.environ.get("PATH").split(":")

    def _search_in_path(self, arg):
        return File.find_exec(self._get_path_dirs(), arg)

    def _shell_builtin(self, arg):
        return arg in commands

    def _print_shell_builtin(self, arg):
        print(arg + " is a shell builtin")

    def _print_exec(self, arg, executable):
        print(arg + " is " + executable.full_path())

    def _print_not_found(self, arg):
        print(arg + ": not found")
             
                
commands = {
    "exit" : ExitCommand,
    "echo" : EchoCommand,
    "type" : TypeCommand
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
        
        
    def _get_path_dirs():
        return os.environ.get("PATH").split(":")

    def _search_in_path( arg ):
        return File.find_exec( _get_path_dirs() , arg)
    
    while True:
                
        next_line = input_next_line()
        next_command = next_line["command"]
                
        if next_command in commands.keys(): 
            commands[next_command](next_line["args"]).run() 
            
        elif (exec := _search_in_path(next_command)):
            subprocess.run(
                [exec.full_path(), *next_line["args"]]
            )         
               
            print(f"Program was passed { len(next_line["args"]) + 1 } args (including program name).")
            
        else:
            print_not_found( next_command )
                  
  
            

if __name__ == "__main__":
    main()
