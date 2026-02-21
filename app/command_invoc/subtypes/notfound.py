import sys
from app.command_invoc.models import CommandInvoc, PipelineResult

def err_not_found(command):
    print(f"{command}: command not found", file=sys.stderr) 

class NotFoundCommandInvoc (CommandInvoc):
    
    def _run_in_child(self, in_fd, out_fd):
        raise Exception("Method rejected. Refactor!")
    
    def _new_proc_in_standalone(self):
        return False
    
    def run(self, stdin):
        err_not_found(
            self.spec().command()
        )
        
        return PipelineResult.no_pipeline()
        
         