from app.command_invoc.models import CommandInvoc, PipelineResult
import sys
import os


STDIN = 0
STDOUT = 1 

class ExecCommandInvoc(CommandInvoc):


    def run(self, stdin):


        #SAME
        def proc_filedescriptors():
            """Return (next_stdin, stdout) for this process stage."""
            return (None, STDOUT) if self.end_pipe() else os.pipe()
        
        #SAME
        def parent_close_fds(out_fd, in_fd):
            """Close file descriptors the parent does not need."""
            if out_fd != STDOUT:
                os.close(out_fd)
            if in_fd != None and in_fd != STDIN :
                os.close(in_fd)
        
        #SAME        
        def run_in_new_proc():
            next_stdin, stdout = proc_filedescriptors()
            child_pid = run_in_child(stdin, stdout)
            parent_close_fds(stdout, stdin)
            return PipelineResult(next_stdin, lambda: os.waitpid(child_pid, 0) )
        
        # DIFF
        def run_in_child(in_fd, out_fd):
            """Fork and run the child logic, exiting immediately."""
            child_pid = os.fork()
            if child_pid == 0:
                
                os.dup2(in_fd, STDIN)
                os.dup2(out_fd, STDOUT)
                os.execvp( self.spec().command() , [ self.spec().command(), *self.spec().args() ] )
                
            return child_pid
        
        

        return run_in_new_proc()  
        
        


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