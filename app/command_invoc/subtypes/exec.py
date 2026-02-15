from app.command_invoc.models import CommandInvoc
import sys
import subprocess
from app.command_invoc.subtypes.buitlin.builtin import PipelineResult


class ExecCommandInvoc(CommandInvoc):


    def run(self, stdin):
        # Start the process
        p = subprocess.Popen(
            [ self.spec().command() , *self.spec().args() ],
            stdin=stdin,
            stdout=sys.stdout if self.end_pipe() else subprocess.PIPE,
            stderr=sys.stderr,
            text=True,  # ensures input/output are str, not bytes
            cwd=self.shell_context().cwd()
        )

        return PipelineResult(p.stdout, lambda : p.wait() )