from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc


class EchoCommand(BuiltinCommandInvoc):

    expected_command="echo"

    def run( self, stdin ):
        print( " ".join( self.spec().args() ) )