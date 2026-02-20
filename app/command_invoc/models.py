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
        
        all_tokens =  Tokenizer().run( self.raw   ) 
        
        return all_tokens[0]

    def args(self):
        
        all_tokens =  Tokenizer().run( self.raw   ) 
        
        return all_tokens[1:]
       
    



        
class Tokens:
    
    def __init__(self):
        self._data = []
        self._new_word = True
        
    def __iter__(self):
        return self._data.__iter__()
    
    def add_char(self, c):
        if self._new_word:
            self._new_word = False
            self._data.append("")

        self._data[-1] += c
            
    def new_word(self):
        self._new_word = True
        
        
        

class Tokenizer:
    
    def __init__(self):
        # -------------------- initialize state --------------------
        self.inside_single_quotes = False
        self.inside_double_quotes = False
        self.in_escape_seq = False


    def _outer_space(self, c):
        return c.isspace() and not self.inside_single_quotes and not self.inside_double_quotes and not self.in_escape_seq

    # predicates
    def _is_closing_single_quote(self, c):
        return c == "'" and self.inside_single_quotes

    def _is_closing_double_quote(self, c):
        return c == '"' and self.inside_double_quotes and not self.in_escape_seq

    def _is_opening_single_quote(self, c):
        return c == "'" and not self.inside_single_quotes and not self.inside_double_quotes and not self.in_escape_seq

    def _is_opening_double_quote(self, c):
        return c == '"' and not self.inside_single_quotes and not self.inside_double_quotes and not self.in_escape_seq

    def _open_single_quote(self):
        self.inside_single_quotes = True

    def _close_single_quote(self):
        self.inside_single_quotes = False

    def _open_double_quote(self):
        self.inside_double_quotes = True

    def _close_double_quote(self):
        self.inside_double_quotes = False

    def _is_start_escape_seq(self, cur, next_chr):
        if cur != "\\":
            return False
        elif self.in_escape_seq:
            return False
        elif self.inside_single_quotes:
            return False
        elif self.inside_double_quotes:
            escaped = ['"', '\\', '$', '`']
            return next_chr in escaped
        else:
            return True

    def _is_end_escape_seq(self, started_escape_seq):
        return self.in_escape_seq and not started_escape_seq

    def _end_escape_seq(self):
        self.in_escape_seq = False

    # -------------------- Main tokenizer --------------------
    def run(self, st):
        tokens = Tokens()
        
        def add_char(tokens, c):
            tokens.add_char(c)

        for index, c in enumerate(st):
            next_chr = st[index + 1] if index + 1 < len(st) else None
            started_escape_seq = False
            
            
            # inner function only for escape start
            def _start_escape_seq():
                self.in_escape_seq = True
                nonlocal started_escape_seq
                started_escape_seq = True


            if self._outer_space(c):
                
                tokens.new_word()


            elif self._is_closing_single_quote(c):
                self._close_single_quote()

            elif self._is_closing_double_quote(c):
                self._close_double_quote()

            elif self._is_opening_single_quote(c):
                self._open_single_quote()

            elif self._is_opening_double_quote(c):
                self._open_double_quote()

            elif self._is_start_escape_seq(c, next_chr):
                _start_escape_seq()

            else:
                add_char(tokens, c)

            if self._is_end_escape_seq(started_escape_seq):
                self._end_escape_seq()

        return list(tokens)





            
        
        
        
        
        
        






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