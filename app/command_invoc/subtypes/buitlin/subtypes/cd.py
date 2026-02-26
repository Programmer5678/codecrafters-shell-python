from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
import os
import sys


def runny(spec, shell_context ):

    def err_no_such_file_dir():
        print(f"cd: {target_path}: No such file or directory", file=sys.stderr)

    def absolute(target_path):

        def is_absolute(path):
            return path[0] == '/'

        def is_home_dir(path):
            return path == "~"

        def home_dir():
            return os.path.expanduser("~")

        if is_absolute(target_path):
            return os.path.abspath(target_path)

        elif is_home_dir(target_path):
            return home_dir()

        else:
            return os.path.abspath(os.path.join(shell_context.cwd() , target_path))



    if( len(spec.args()) > 1 ):
        print("cd: too many arguments")

    target_path=spec.args()[0]
    target_full_path = absolute(target_path)

    if os.path.isdir(target_full_path):
        shell_context.setcwd(target_full_path)

    else:
        err_no_such_file_dir()
        
    return shell_context 


class Runner:
    
    def __init__(self, spec, shell_context):
        self._spec = spec
        self._shell_context = shell_context
        self._future_shell_context = None
        
    def start(self):
        self._future_shell_context = runny(self._spec, self._shell_context)
        
    def future_shell_context(self):
        return self._future_shell_context

class CdCommand(BuiltinCommandInvoc):

    expected_command="cd"

    def run_core(self):
        runner = Runner(self.spec(), self.shell_context())
        return runner