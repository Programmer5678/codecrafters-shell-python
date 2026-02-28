from contextlib import contextmanager
from app.command_invoc.models import CommandInvoc
from app.command_invoc.invoc_runner import InvocRunner
import os

STDIN = 0
STDOUT = 1 

    
class ExecRunner(InvocRunner):
    def run(self):
        os.chdir( self._shell_context.cwd() )
        os.execvp(
            self._spec.command(),
            [self._spec.command(), *self._spec.args()]
        )
    
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
            runner = ExecRunner(self.spec(), self.shell_context())
            return runner

        
        