from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc


class HistoryCommand(BuiltinCommandInvoc):

    expected_command = "history"

    def run(self, stdin):

        def history_line(line_num, line_content):
            return f"\t{line_num+1} {line_content}"

        def print_all_lines(history_lines):
            print(   "\n".join( history_lines )   )

        def print_last_n_lines(history_lines, nl):
            print(   "\n".join( history_lines[-nl:] )   )

        def no_num_lines_arg():
            return len( self.spec().args() ) == 0

        def num_lines_arg():
            return int(self.spec().args()[0])

        def too_many_args():
            return len( self.spec().args() ) > 1

        def err_too_many_args():
            print("history: too many arguments", file=sys.stderr)

        history_lines = [ history_line(line_num, line) for line_num, line in enumerate( self.shell_context().history() ) ]

        if no_num_lines_arg():
            print_all_lines(history_lines)

        elif too_many_args():
            err_too_many_args()

        else:
            print_last_n_lines( history_lines, num_lines_arg() )