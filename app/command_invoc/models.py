from dataclasses import dataclass
from typing import Any
from app.search_files import find_in_path
import copy
from abc import ABC, abstractmethod


class CommandInvocSpec:

    def __init__( self, command_invoc_str ):
        self.command_invoc_str = command_invoc_str

    def __repr__(self):
        return self.command_invoc_str

    def command(self):
        return self.command_invoc_str.split()[0]

    def args(self):
        return self.command_invoc_str.split()[1:]


@dataclass
class CommandInvocArgs:
    spec : CommandInvocSpec
    end_pipe : bool
    shell_context: Any


class CommandInvoc(ABC):

    def __init__( self, args: CommandInvocArgs):
        self._spec = args.spec
        self._end_pipe = args.end_pipe
        self._shell_context = copy.deepcopy(args.shell_context)

    def spec(self):
        return self._spec

    def end_pipe(self):
        return self._end_pipe

    def shell_context(self):
        return self._shell_context

    def setcwd(self, cwd):
        self._shell_context.setcwd(cwd)


    @abstractmethod
    def run(self, stdin):
        pass


    @classmethod
    def resolve(cls, args: CommandInvocArgs ):

        from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
        from app.command_invoc.subtypes.exec import ExecCommandInvoc
        from app.command_invoc.subtypes.notfound import NotFoundCommandInvoc

        if BuiltinCommandInvoc.is_builtin( args.spec.command() ):
            return BuiltinCommandInvoc.resolve( args )

        elif find_in_path( args.spec.command() ) :
            return ExecCommandInvoc( args )
        else:
            return NotFoundCommandInvoc(args)