from app.command_invoc.files.absolute_path import absolute
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from app.command_invoc.invoc_runner import InvocRunner
import os
import sys







    
class CdRunner(InvocRunner):
    
    def run(self):

        def err_no_such_file_dir():
            print(f"cd: {target_path}: No such file or directory", file=sys.stderr)

        if( len(self._spec.args()) > 1 ):
            print("cd: too many arguments")

        target_path=self._spec.args()[0]
        target_full_path = absolute(target_path, self._shell_context.cwd())

        if os.path.isdir(target_full_path):
            self._shell_context.setcwd(target_full_path)

        else:
            err_no_such_file_dir()
            
        return self._shell_context 

    
class CdCommand(BuiltinCommandInvoc):

    expected_command="cd"

    def run_core(self):
        runner = CdRunner(self.spec(), self.shell_context())
        return runner