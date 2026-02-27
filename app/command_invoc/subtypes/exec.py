from contextlib import contextmanager

from app.command_invoc.models import CommandInvoc
import sys
import os


STDIN = 0
STDOUT = 1 

def runny(spec, shell_context):  
    os.execvp(
            spec.command(),
            [spec.command(), *spec.args()]
        )
    
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

        
class Runner:
    
    def __init__(self, spec, shell_context):
        self._spec = spec
        self._shell_context = shell_context
        self._updated_end_shell_context = ShellContextUpdate.no_update()
        
    def start(self):
        res = runny(self._spec, self._shell_context)
        if res != None:
            self._updated_end_shell_context = ShellContextUpdate.new( res )        
        
    def updated_end_shell_context(self):
        return self._updated_end_shell_context
    
    
class ExecCommandInvoc(CommandInvoc):


    def _new_proc_in_standalone(self):
        return True


    @contextmanager
    def child_fd_setup(self, in_fd, out_fd):
        # Duplicate FDs so the child uses them as stdin/stdout
        os.dup2(in_fd, STDIN)
        os.dup2(out_fd, STDOUT)

        # Optional: close original FDs after dup2
        if in_fd not in (None, STDIN):
            os.close(in_fd)
        if out_fd != STDOUT:
            os.close(out_fd)
            
        yield

    def run_core(self):
            runner = Runner(self.spec(), self.shell_context())
            return runner

        
        