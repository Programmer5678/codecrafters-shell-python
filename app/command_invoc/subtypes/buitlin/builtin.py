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
            fd = os.open(self._redirect_to, os.O_RDWR)
            self.run_core( fd )
            result = PipelineResult.no_pipeline()

        return result


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
    def resolve_subclass(cls, args: CommandInvocArgs):

        def command_class( command ):
            return cls.commands()[command]

        # CommandClass = globals()[command_class( args.spec.command() ) ]      
        return command_class( args.spec.command()  ) ( args )  # new command