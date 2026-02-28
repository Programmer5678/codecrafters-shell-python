
from app.command_invoc.files.absolute_path import absolute
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
import os
import sys
from app.shell import add_history
from app.command_invoc.invoc_runner import InvocRunner


class HistoryRunner(InvocRunner):

    def run(self):
        num_args = len(self._spec.args())

        if num_args == 0:
            self._run_no_args()

        elif num_args == 1:
            self._run_one_arg()

        elif num_args == 2:
            self._run_two_args()

        else:
            self._err_too_many_args()

        return self._shell_context


    # ---------- case: no args ----------
    def _run_no_args(self):
        history_lines = [
            f"\t{i+1} {line}"
            for i, line in enumerate(self._shell_context.history())
        ]

        print("\n".join(history_lines) + "\n", end="")


    # ---------- case: one arg ----------
    def _run_one_arg(self):
        try:
            nl = int(self._spec.args()[0])
        except ValueError:
            return

        history_lines = [
            f"\t{i+1} {line}"
            for i, line in enumerate(self._shell_context.history())
        ]

        os.write(1, ("\n".join(history_lines[-nl:]) + "\n").encode())


    # ---------- case: two args ----------
    def _run_two_args(self):
        flag, file = self._spec.args()
        full_path = absolute( file, self._shell_context.cwd() )

        def read_history(read_from):
            # print(os.getcwd())
            with open(read_from, "r") as f:
                lines = [l.strip() for l in f.readlines()]
                for line in lines:
                    if line:
                        add_history(self._shell_context, line)

        def write_history(write_to):
            with open(write_to, "w") as f:
                print("\n".join(self._shell_context.history()), file=f)
                
                
        def append_history(append_to):
            with open(append_to, "a") as f:
                since_last_append = self._shell_context.history()[self._shell_context.last_append_history:]
                print("\n".join( since_last_append ), file=f)
                
            self._shell_context.last_append_history = len(self._shell_context.history())
                

        if flag == "-r":
            read_history(full_path)

        elif flag == "-w":
            write_history(full_path)
            
        elif flag == "-a":
            append_history(full_path)

        else:
            print("history: invalid arg " + flag, file=sys.stderr)


    # ---------- helpers ----------
    def _err_too_many_args(self):
        print("history: too many arguments", file=sys.stderr)
        

class HistoryCommand(BuiltinCommandInvoc):

    expected_command = "history"

    def run_core(self):
        runner = HistoryRunner(self.spec(), self.shell_context())
        return runner
        
                   
        
        
                