import sys
from app.command_invoc.models import CommandInvoc

def err_not_found(command):
    print(f"{command}: command not found", file=sys.stderr) 

class NotFoundCommandInvoc (CommandInvoc):
    
    def _run_in_child(self, in_fd, out_fd):
        raise Exception("FUCK")
    
    def run(self, stdin):
        return err_not_found(
            self.spec().command()
        )