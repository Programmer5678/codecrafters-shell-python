from app.command_invoc.models import CommandInvoc, PipelineResult
import sys
import os


STDIN = 0
STDOUT = 1 

class ExecCommandInvoc(CommandInvoc):


    def run(self, stdin):
        """Main run function that either spawns a child process or returns a pipeline result."""
        return self._run_in_new_proc(stdin)


    def _run_in_child(self, in_fd, out_fd):
        """Fork and run the child logic, exiting immediately."""
        child_pid = os.fork()

        if child_pid == 0:
            # Duplicate FDs so the child uses them as stdin/stdout
            os.dup2(in_fd, STDIN)
            os.dup2(out_fd, STDOUT)

            # Optional: close original FDs after dup2
            if in_fd not in (None, STDIN):
                os.close(in_fd)
            if out_fd != STDOUT:
                os.close(out_fd)

            # Replace child process with the target command
            os.execvp(
                self.spec().command(),
                [self.spec().command(), *self.spec().args()]
            )

        return child_pid
