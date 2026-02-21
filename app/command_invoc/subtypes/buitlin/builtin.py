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
        
        
    def _new_proc_in_standalone(self):
        return False

    def child_fd_setup(self, in_fd, out_fd):
        """run the child logic, exiting immediately."""

        try:
            os.dup2(out_fd, 1)
            yield
        finally:
            if out_fd != STDOUT:
                os.close(out_fd)
            os._exit(0)
        
    
    
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