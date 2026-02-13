from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc


class PwdCommand(BuiltinCommandInvoc):

    expected_command="pwd"

    def run(self, stdin):
        print( self.shell_context().cwd() )