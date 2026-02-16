from app.command_invoc.models import CommandInvoc, CommandInvocArgs, PipelineResult
import os
from abc import abstractmethod



STDIN = 0
STDOUT = 1    

class BuiltinCommandInvoc(CommandInvoc):

    def __init__(self, args : CommandInvocArgs):
        super().__init__(args)

        def command_matches_expected():
            return self.expected_command == args.spec.command()
        assert( command_matches_expected()  )
        
        
        
    
    def run(self, stdin):
        if self.in_pipe():
            result = self._run_in_new_proc(stdin)
        else:
            self.run_core(STDOUT)
            result = PipelineResult(None, lambda: None)

        return result


    def _proc_filedescriptors(self):
        """Return (next_stdin, stdout) for this process stage."""
        return (None, STDOUT) if self.end_pipe() else os.pipe()


    def _run_in_child(self, in_fd, out_fd):
        """Fork and run the child logic, exiting immediately."""
        child_pid = os.fork()
        if child_pid == 0:
            try:
                self.run_core(out_fd)
            finally:
                if out_fd != STDOUT:
                    os.close(out_fd)
                os._exit(0)
        return child_pid


    def _parent_close_fds(self, out_fd, in_fd):
        """Close file descriptors the parent does not need."""
        if out_fd != STDOUT:
            os.close(out_fd)
        if in_fd is not None and in_fd != STDIN:
            os.close(in_fd)


    def _run_in_new_proc(self, stdin):
        next_stdin, stdout = self._proc_filedescriptors()
        child_pid = self._run_in_child(stdin, stdout)
        self._parent_close_fds(stdout, stdin)
        return PipelineResult(next_stdin, lambda: os.waitpid(child_pid, 0))
    
    
    

        
    @abstractmethod
    def run_core(self, out):
        pass
        """The core of the run, without all the process and pipe management"""
    
    @classmethod
    def commands(cls):
        
        return {
            Subclass.expected_command : Subclass
            for Subclass in cls.__subclasses__()
        }

    @classmethod
    def is_builtin(cls, command):
        return command in cls.commands().keys()


    @classmethod
    def resolve(cls, args: CommandInvocArgs):

        def command_class( command ):
            return cls.commands()[command]

        # CommandClass = globals()[command_class( args.spec.command() ) ]      
        return command_class( args.spec.command()  ) ( args )  # new command