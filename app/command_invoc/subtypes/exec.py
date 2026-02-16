from app.command_invoc.models import CommandInvoc, PipelineResult
import sys
import os


STDIN = 0
STDOUT = 1 

class ExecCommandInvoc(CommandInvoc):


    def run(self, stdin):
        """Main run function that either spawns a child process or returns a pipeline result."""
        return self._run_in_new_proc(stdin)


    def _proc_filedescriptors(self):
        """Return (next_stdin, stdout) for this process stage."""
        return (None, STDOUT) if self.end_pipe() else os.pipe()


    def _parent_close_fds(self, out_fd, in_fd):
        """Close file descriptors the parent does not need."""
        if out_fd != STDOUT:
            os.close(out_fd)
        if in_fd is not None and in_fd != STDIN:
            os.close(in_fd)


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


    def _run_in_new_proc(self, stdin):
        """Set up the pipe, spawn child, and return a PipelineResult."""
        next_stdin, stdout = self._proc_filedescriptors()
        child_pid = self._run_in_child(stdin, stdout)
        self._parent_close_fds(stdout, stdin)
        return PipelineResult(next_stdin, lambda: os.waitpid(child_pid, 0)) 
        
        


    # def run(self, stdin):
    #     # Start the process
    #     p = subprocess.Popen(
    #         [ self.spec().command() , *self.spec().args() ],
    #         stdin=stdin,
    #         stdout=sys.stdout if self.end_pipe() else subprocess.PIPE,
    #         stderr=sys.stderr,
    #         text=True,  # ensures input/output are str, not bytes
    #         cwd=self.shell_context().cwd()
    #     )

    #     return PipelineResult(p.stdout, lambda : p.wait() )