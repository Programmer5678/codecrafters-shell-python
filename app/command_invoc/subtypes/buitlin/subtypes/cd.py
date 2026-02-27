from app.command_invoc.models import NextLineShellContext
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
import os
import sys






class ShellContextUpdate:
    def __init__(self, value, is_update):
        self._value = value
        self._is_update = is_update

    @classmethod
    def no_update(cls):
        return cls(None, False)

    @classmethod
    def new(cls, value):
        return cls(value, True)

    def is_update(self):
        return self._is_update

    def value(self):
        return self._value
 
 
from abc import ABC, abstractmethod       
class InvocRunner(ABC):
    
    def __init__(self, spec, shell_context):
        self._spec = spec
        self._shell_context = shell_context
        self._updated_end_shell_context = ShellContextUpdate.no_update()
        
    @abstractmethod 
    def runny(self):
        pass
        
    
    def start(self):
        res = self.runny()
        if res != None:
            self._updated_end_shell_context = ShellContextUpdate.new( res )        
        
    def updated_end_shell_context(self):
        return self._updated_end_shell_context
    
class CdRunner(InvocRunner):
    
    def runny(self ):

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
                return os.path.abspath(os.path.join(self._shell_context.cwd() , target_path))



        if( len(self._spec.args()) > 1 ):
            print("cd: too many arguments")

        target_path=self._spec.args()[0]
        target_full_path = absolute(target_path)

        if os.path.isdir(target_full_path):
            self._shell_context.setcwd(target_full_path)

        else:
            err_no_such_file_dir()
            
        return self._shell_context 

    
class CdCommand(BuiltinCommandInvoc):

    expected_command="cd"

    def run_core(self):
        runner = CdRunner(self.spec(), self.shell_context())
        return runner