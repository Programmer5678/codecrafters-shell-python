import sys
import os 

from abc import ABC, abstractmethod

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
        exit(0)
    
class EchoCommand(Command):
    def run( self ):
        print( " ".join( self.args() ) )
     




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
    
    # @classmethod
    # def find_exec(cls, dir_paths, file):
    #     for file in File._all_files:
    #         if os.access(f2, os.X_OK)
        
             
        
class TypeCommand(Command):
    
    def run(self):
        for arg in self.args():
            
            if arg in commands.keys():
                print(arg + " is a shell builtin")
                
            else: 
                
                output = arg + ": not found"
                
                path = os.environ.get("PATH")
            
                        
                for file in File._all_files( path.split(":") ):
                        
                    if file.file() == arg and os.access(file.full_path(), os.X_OK): 
                        output = arg + " is " + file.full_path()
                        
                
                print(output)
                
commands = {
    "exit" : ExitCommand,
    "echo" : EchoCommand,
    "type" : TypeCommand
}
    
def main():
    
    while True:
        print("$ ", end="", flush=True)
        line = sys.stdin.readline()
        command = line.split()[0]
        args = line.split()[1:]
                
        if command in commands.keys():
            commands[command](args).run()           
  
        else:
            print(f"{command}: command not found")
    


if __name__ == "__main__":
    main()
