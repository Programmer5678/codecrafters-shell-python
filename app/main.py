import os 

from abc import ABC, abstractmethod
import subprocess


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
        print("\n".join([ f"\t{line_num+1} {line}" for line_num, line in enumerate( self.shell_context.history() ) ] ))
 
 
        
class NotCommand(Command):
    
    def __init__(self, shell_context, command):
        self.shell_context = shell_context
        self.command = command
        
    
    def run(self):
        print_not_found(self.command)
        

class ProgramCommand(Command):
    
    def __init__(self, shell_context, command, args):
        self.shell_context = shell_context
        self.command = command
        self.args = args
        
    def run(self):
        subprocess.run(
                [self.command, *self.args],
                cwd=self.shell_context.cwd()
            )    
        
        
                
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


def print_not_found(command):
    print(f"{command}: command not found")
    
def main():
        
    def input_next_line():
        
        def empty_line(line):
            return line == None or len(line.split()) == 0
        
        def command(line):
            return line.split()[0]
        
        def args(line):
            return line.split()[1:]
        
        line = None
        while empty_line(line):
            print("$ ", end="", flush=True)
            line = input()
            
        return { "command" : command(line), "args": args(line)}
            
    
    
        
       
        


    
    shell_context = ShellContext( os.getcwd(), [] )
    
    while True:
                
        next_line = input_next_line()
        next_command = next_line["command"]
        history = shell_context.history() + [ next_line["command"] + " " + " ".join(next_line["args"]) ]
        shell_context = ShellContext( shell_context.cwd(), history )
                
        if next_command in commands.keys(): 
            com = commands[next_command] ( next_line["args"], shell_context )
            com.run()
            shell_context = ShellContext(com.shell_context.cwd(), shell_context.history() )
        
        
        elif File.find_in_path(next_command) :
            com = ProgramCommand(shell_context, next_command, next_line["args"] )  
            com.run()    
                           
        else:
            com = NotCommand(shell_context, next_command)
            com.run()
                  


if __name__ == "__main__":
    main()