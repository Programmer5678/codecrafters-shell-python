from dataclasses import dataclass
import itertools
import os
from typing import Any
from app.search_files import find_in_path
import copy
from abc import ABC, abstractmethod



class PipelineResult:

    def __init__(self, next_stdin, child_wait):
        self._next_stdin = next_stdin
        self._child_wait = child_wait
        
    def next_stdin(self):
        return self._next_stdin
    
    def child_wait(self):
        return self._child_wait


class CommandInvocSpec:

    def __init__( self, raw ):
        self.raw = raw

    def __repr__(self):
        return self.raw

    def command(self):
        return self.raw.split()[0]

    def args(self):
        
        SINGLE_QUOTE = "'"
        DOUBLE_QUOTE = '"'
        
        def tokenize(st):
            
            def add_char(result, c):
                if not result:
                    result.append("")
                result[0] += c

            def outer_space(c):
                return c.isspace() and ( outside_single_quotes and outside_double_quotes )

            result = []
            outside_single_quotes = True
            outside_double_quotes = True

            for index, c in enumerate(st):
                if outer_space(c):
                    result += tokenize(st[index + 1:])
                    break
                else:
                    add_char(result, c)

                if c == SINGLE_QUOTE and not outside_single_quotes:
                    outside_single_quotes = True
                    
                if c == DOUBLE_QUOTE and not outside_double_quotes:
                    outside_double_quotes = True
                    
                if outside_double_quotes and outside_single_quotes:
                    if c == SINGLE_QUOTE:
                        outside_single_quotes = False
                    if c == DOUBLE_QUOTE:
                        outside_double_quotes = False

            return result
        
        def remove_quotes(tokens):
            
            def _remove_quotes_from_str(s):
                return "".join(c for c in s if c != SINGLE_QUOTE and c != DOUBLE_QUOTE)
            
            return [ _remove_quotes_from_str(token) for token in tokens]
        
        all_tokens = remove_quotes( tokenize( self.raw   ) )
        
        return all_tokens[1:]
       
                
        
        
        






@dataclass
class CommandInvocArgs:
    spec : CommandInvocSpec
    in_pipe : bool
    end_pipe : bool
    shell_context: Any



STDIN = 0
STDOUT = 1

class CommandInvoc(ABC):

    def __init__( self, args: CommandInvocArgs):
        self._spec = args.spec
        self._end_pipe = args.end_pipe
        self._shell_context = copy.deepcopy(args.shell_context)
        self._in_pipe = args.in_pipe

    def spec(self):
        return self._spec

    def in_pipe(self):
        return self._in_pipe

    def end_pipe(self):
        return self._end_pipe

    def shell_context(self):
        return self._shell_context

    def setcwd(self, cwd):
        self._shell_context.setcwd(cwd)


    @abstractmethod
    def run(self, stdin):
        pass
    
    @abstractmethod
    def _run_in_child(in_fd, out_fd):
        pass
    
    def _proc_filedescriptors(self):
        """Return (next_stdin, stdout) for this process stage."""
        return (None, STDOUT) if self.end_pipe() else os.pipe()

    def _parent_close_fds(self, out_fd, in_fd):
        """Close file descriptors the parent does not need."""
        if out_fd != STDOUT:
            os.close(out_fd)
        if in_fd is not None and in_fd != STDIN:
            os.close(in_fd)
            
    def _run_in_new_proc(self, stdin):
        """Set up the pipe, spawn child, and return a PipelineResult."""
        next_stdin, stdout = self._proc_filedescriptors()
        child_pid = self._run_in_child(stdin, stdout)
        self._parent_close_fds(stdout, stdin)
        return PipelineResult(next_stdin, lambda: os.waitpid(child_pid, 0)) 
    
    def _run_in_new_proc(self, stdin):
        next_stdin, stdout = self._proc_filedescriptors()
        child_pid = self._run_in_child(stdin, stdout)
        self._parent_close_fds(stdout, stdin)
        return PipelineResult(next_stdin, lambda: os.waitpid(child_pid, 0))

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