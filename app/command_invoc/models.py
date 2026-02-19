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
        
        all_tokens =  _tokenize( self.raw   ) 
        
        return all_tokens[1:]
       
       
def _tokenize(st):
        
        SINGLE_QUOTE = "'"
        DOUBLE_QUOTE = '"'
        BACKSLASH = "\\"

        def add_char(result, c):
            if not result:
                result.append("")
            result[0] += c

        def outer_space(c, in_escape_seq):
            return c.isspace() and outside_single_quotes and outside_double_quotes and not in_escape_seq

        # predicates
        def is_closing_single_quote(c):
            return c == SINGLE_QUOTE and not outside_single_quotes

        def is_closing_double_quote(c, in_escape_seq):
            return c == DOUBLE_QUOTE and not outside_double_quotes and not in_escape_seq

        def is_opening_single_quote(c, in_escape_seq):
            return c == SINGLE_QUOTE and outside_single_quotes and outside_double_quotes and not in_escape_seq

        def is_opening_double_quote(c, in_escape_seq):
            return c == DOUBLE_QUOTE and outside_single_quotes and outside_double_quotes and not in_escape_seq

        # actions
        def open_single_quote():
            nonlocal outside_single_quotes
            outside_single_quotes = False

        def close_single_quote():
            nonlocal outside_single_quotes
            outside_single_quotes = True

        def open_double_quote():
            nonlocal outside_double_quotes
            outside_double_quotes = False

        def close_double_quote():
            nonlocal outside_double_quotes
            outside_double_quotes = True
        
        result = []
        outside_single_quotes = True
        outside_double_quotes = True
        
        in_escape_seq = False

        for index, c in enumerate(st):

            
            
            def tokenize_remaining():
                return _tokenize(st[index + 1:])
            
            def is_start_escape_seq(cur, in_escape_seq, next_chr):
                
                if cur != BACKSLASH:
                    return False
                elif in_escape_seq:
                    return False                
                elif outside_single_quotes and outside_double_quotes:
                    return True
                elif not outside_single_quotes:
                    return False
                elif not outside_double_quotes:
                    return next_chr in [DOUBLE_QUOTE, BACKSLASH, '$', '`']
                
                    
            
            def start_escape_seq():
                nonlocal in_escape_seq
                nonlocal started_escape_seq
                in_escape_seq = True
                started_escape_seq = True
            
            def is_end_escape_seq(in_escape_seq, started_escape_seq):
                return in_escape_seq and not started_escape_seq # If we are in escape sequence that we didnt just start, end it
            
            def end_escape_seq():
                nonlocal in_escape_seq
                in_escape_seq = False
                
            started_escape_seq = False
            next_chr = st[index] if index < len(st) else None

            if outer_space(c, in_escape_seq):
                result += tokenize_remaining()
                break

            elif is_closing_single_quote(c):
                close_single_quote()

            elif is_closing_double_quote(c, in_escape_seq):
                close_double_quote()

            elif is_opening_single_quote(c, in_escape_seq): 
                open_single_quote()

            elif is_opening_double_quote(c, in_escape_seq):
                open_double_quote()

            elif is_start_escape_seq(c, in_escape_seq, next_chr):
                start_escape_seq()
                
            else:  
                add_char(result, c)
            
            if is_end_escape_seq(in_escape_seq, started_escape_seq):
                end_escape_seq()
                

        return result
            
        
        
        
        
        
        






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