from app.command_invoc.models import CommandInvoc
from app.main import err_not_found


class NotFoundCommandInvoc (CommandInvoc):
    def run(self, stdin):
        return err_not_found(
            self.spec().command()
        )