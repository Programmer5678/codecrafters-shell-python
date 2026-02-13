from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc


class ExitCommand(BuiltinCommandInvoc):

    expected_command = "exit"

    def run( self, stdin ):
        raise SystemExit(0)