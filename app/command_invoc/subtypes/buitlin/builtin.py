from app.command_invoc.models import CommandInvoc, CommandInvocArgs


class BuiltinCommandInvoc(CommandInvoc):

    def __init__(self, args : CommandInvocArgs):
        super().__init__(args)

        def command_matches_expected():
            return self.expected_command == args.spec.command()
        assert( command_matches_expected()  )

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