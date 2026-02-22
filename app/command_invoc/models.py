from dataclasses import dataclass
import itertools
import os
from typing import Any
from app.command_invoc.tokenize import tokenize
from app.search_files import find_in_path
import copy
from abc import ABC, abstractmethod



class PipelineResult:

    def __init__(self, next_stdin, child_wait):
        self._next_stdin = next_stdin
        self._child_wait = child_wait
        
    @classmethod
    def no_pipeline(cls):
        return cls(None, lambda : None) 
        
    def next_stdin(self):
        return self._next_stdin
    
    def wait_child_end(self):
        return self._child_wait







class CommandInvocSpec:

    def __init__( self, raw ):
        self.raw = raw

    def __repr__(self):
        return self.raw

    def command(self):
        
        all_tokens =  tokenize( self.raw   ) 
        
        return all_tokens[0]

    def args(self):
        
        all_tokens =  tokenize( self.raw   ) 
        
        return all_tokens[1:]
       
    








        

@dataclass
class CommandInvocArgs:
    spec : CommandInvocSpec
    position : Any
    shell_context: Any
    redirect_to: str



STDIN = 0
STDOUT = 1


class LinePosition:
    
    def __init__ (self, in_pipe, last_invoc):
        
        self._last_invoc =  last_invoc
        self._in_pipe = in_pipe
        
        
    def in_pipe(self):
        return self._in_pipe

    def last_invoc(self):
        return self._last_invoc
        

class CommandInvoc(ABC):

    def __init__( self, args: CommandInvocArgs):
        self._spec = args.spec
        
        self.position = args.position
        
        self._shell_context = copy.deepcopy(args.shell_context)
        self._redirect_to = args.redirect_to

    def spec(self):
        return self._spec

    def in_pipe(self):
        return self.position.in_pipe()

    def last_invoc(self):
        return self.position.last_invoc()

    def shell_context(self):
        return self._shell_context

    def setcwd(self, cwd):
        self._shell_context.setcwd(cwd)


    def run(self, in_fd):
        
        next_in_fd , out_fd = self._file_descriptors()
        
            
        if self._in_new_proc(): #If need 
            
            """Set up the pipe, spawn child, and return a PipelineResult."""
            
            child_pid = os.fork()
            in_child_proc = (child_pid == 0)
            if in_child_proc: # if child
                #Run in child
                self._run_in_child(in_fd, out_fd)
                
            else:
            
                self._parent_close_fds(out_fd, in_fd)
                wait_child_close = lambda: os.waitpid(child_pid, 0) # Wait func - wait for child to close
                        
        else:
                        
            self._run_in_parent(in_fd, out_fd)
            
            nothing_func = lambda : None
            wait_child_close = nothing_func

        return PipelineResult(next_in_fd, wait_child_close)
    
    def _run_in_child(self, in_fd, out_fd):
        with self.child_fd_setup(in_fd, out_fd):
            self.run_core()
            
    def _run_in_parent(self, in_fd, out_fd):
        
        def cur_stdout():
            return os.dup(STDOUT)
        
        def set_output_to_fd(out_fd):
            os.dup2(out_fd, STDOUT)
        
        def reset_output_to_stdout(save_stdout):
            os.dup2(save_stdout, STDOUT)
        
        try:
            save_stdout = cur_stdout() 
            set_output_to_fd(out_fd) 
            
            self.run_core()
           
        finally:   
            reset_output_to_stdout(save_stdout)
    
    def _in_new_proc(self):
        return self.in_pipe() or self._new_proc_in_standalone()
    
    def _file_descriptors(self):
        if self._redirect_to:
            next_in_fd = None
            out_fd = os.open(self._redirect_to, os.O_RDWR | os.O_CREAT)

        elif not self.last_invoc():
            next_in_fd, out_fd = os.pipe()
            
        else:
            next_in_fd = None
            out_fd = STDOUT
            
        return next_in_fd, out_fd
    
    
    
    @abstractmethod
    def _new_proc_in_standalone(self):
        pass
    

    
    @abstractmethod
    def run_core(self):
        pass
        """The core of the run, without all the process and pipe management"""
    
    abstractmethod
    def child_fd_setup(self):
        pass
    
    

    def _parent_close_fds(self, out_fd, in_fd):
        """Close file descriptors the parent does not need."""
        if out_fd != STDOUT:
            os.close(out_fd)
        if in_fd is not None and in_fd != STDIN:
            os.close(in_fd)
        
    

    @classmethod
    def resolve_subclass(cls, args: CommandInvocArgs ):

        from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
        from app.command_invoc.subtypes.exec import ExecCommandInvoc
        from app.command_invoc.subtypes.notfound import NotFoundCommandInvoc

        if BuiltinCommandInvoc.is_builtin( args.spec.command() ):
            return BuiltinCommandInvoc.resolve_subclass( args )

        elif find_in_path( args.spec.command() ) :
            return ExecCommandInvoc( args )
        else:
            return NotFoundCommandInvoc(args)