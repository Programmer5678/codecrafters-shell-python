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

    def __init__( self, command_invoc_str ):
        self.command_invoc_str = command_invoc_str
        # print("Args: ", self.args())

    def __repr__(self):
        return self.command_invoc_str

    def command(self):
        return self.command_invoc_str.split()[0]

    def args(self):
        
        def collapse(l):
            res = []
            for item in l:
                if isinstance(item, list):
                    for el in collapse(item):
                        res.append(el)
                else:
                    res.append(item)
            return res
        
        s = self.command_invoc_str    
        
        l = s.split(r"'")
        
        for i in range(len(l)):
            if i % 2 == 0:
                l[i] = l[i].split()       
        l = collapse(l) #collapse list
        
        return l[1:]
       
                
        
        
        






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