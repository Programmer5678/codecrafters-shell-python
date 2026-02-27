from app.command_invoc.models import NextLineShellContext
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc

from multiprocessing import Process
import os



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

class PwdRunner(InvocRunner):
    def runny(self):
        os.write(1, (self._shell_context.cwd() + "\n").encode())
        
class PwdCommand(BuiltinCommandInvoc):
    expected_command = "pwd"

    def run_core(self):
        runner = PwdRunner(self.spec(), self.shell_context())
        return runner
