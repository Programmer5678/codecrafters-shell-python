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
        
class TypeCommand(Command):
    
    def run(self):
        for arg in self.args():
            if arg in commands.keys():
                print(arg + " is a shell builtin")
                
            else: 
                
                output = arg + ": not found"
                
                path = os.environ.get("PATH")
                
                for p in path.split(":"):
                    
                    if os.path.isdir(p):
                        
                        for f in os.listdir(p):
                            
                            f2 = os.path.join(p, f)
                            
                            if f == arg and os.path.isfile( f2 ) and os.access(f2, os.X_OK) : 
                                output = arg + " is " + f2
                
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
