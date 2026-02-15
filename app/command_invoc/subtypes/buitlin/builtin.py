from app.command_invoc.models import CommandInvoc, CommandInvocArgs
import os
from abc import abstractmethod




class PipelineResult:

    def __init__(self, next_stdin, child_wait):
        self._next_stdin = next_stdin
        self._child_wait = child_wait
        
    def next_stdin(self):
        return self._next_stdin
    
    def child_wait(self):
        return self._child_wait


STDOUT = 1    

class BuiltinCommandInvoc(CommandInvoc):

    def __init__(self, args : CommandInvocArgs):
        super().__init__(args)

        def command_matches_expected():
            return self.expected_command == args.spec.command()
        assert( command_matches_expected()  )
        
    
    def run(self, stdin):

        def proc_fds():
            """Return (next_stdin, stdout) for this process stage."""
            return (None, STDOUT) if self.end_pipe() else os.pipe()

        def run_in_child(out_fd):
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

        def parent_close_fds(out_fd, in_fd):
            """Close file descriptors the parent does not need."""
            if out_fd != STDOUT:
                os.close(out_fd)
            if in_fd:
                os.close(in_fd)

        if self.in_pipe():
            next_stdin, stdout = proc_fds()
            child_pid = run_in_child(stdout)
            parent_close_fds(stdout, stdin)
            return PipelineResult( next_stdin, lambda: os.waitpid(child_pid, 0) )
        else:
            self.run_core(STDOUT)
            return PipelineResult(None, lambda: None)
        
        
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