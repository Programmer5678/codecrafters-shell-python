from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
import itertools
import os
from typing import Any
from app.command_invoc.open_files import open_append, open_write
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





class RedirectMode(Enum):
    WRITE = "w"
    APPEND = "a"

class RedirectTarget:
    
    def __init__(self, file : str, mode : RedirectMode):
        self.file = file
        self.mode = mode

        


class CommandInvocSpec:

    def __init__( self, raw ):
        
        def partition_redirects(tokens):
            
            main = []
            redirect_stdout = None
            append_stdout = False
            redirect_stderr = None
            append_stderr = False
            
            index = 0
            while index < len( tokens ):
                cur = tokens[index]
                
                def skip_redirect_iter():
                    nonlocal index
                    index += 2
                
                def is_stdout_redirect(c):
                    return c == "1>" or c == ">"
                
                def is_stdout_append(c):
                    return c == "1>>" or c == ">>"
                
                def stdout_redirect_action():
                    nonlocal redirect_stdout
                    nonlocal tokens
                    nonlocal index
                    
                    next_token = tokens[index + 1]
                    redirect_stdout = next_token
                    skip_redirect_iter()
                    
                def stderr_redirect_action():
                    
                    nonlocal redirect_stderr
                    nonlocal tokens
                    nonlocal index
                    
                    next_token = tokens[index + 1]
                    redirect_stderr = next_token
                    skip_redirect_iter()
                
                def is_stderr_redirect(c):
                    return c == "2>"
                
                def is_stderr_append(c):
                    return c == "2>>"
                
                if is_stdout_redirect(cur):
                    stdout_redirect_action()
                    
                elif is_stdout_append(cur):
                    stdout_redirect_action()
                    append_stdout = True
                    
                                        
                elif is_stderr_redirect(cur):
                    stderr_redirect_action()
                    
                elif is_stderr_append(cur):
                    stderr_redirect_action()
                    append_stderr = True
                    
                else:
                    main.append( cur )
                    
                    def advance_loop():
                        nonlocal index
                        index += 1
                        
                    advance_loop()
                    
            rt_stdout = RedirectTarget( redirect_stdout , RedirectMode.APPEND if append_stdout else RedirectMode.WRITE ) if redirect_stdout else None
            rt_stderr = RedirectTarget( redirect_stderr , RedirectMode.APPEND if append_stderr else RedirectMode.WRITE ) if redirect_stderr else None
            
            return main, rt_stdout, rt_stderr
            
        self.raw = raw
        self._tokens = tokenize(self.raw)
        self._main_part , self.rt_stdout, self.rt_stderr = partition_redirects(self._tokens) 
                    

    def __repr__(self):
        return self.raw

    def command(self):
        
        return self._main_part[0]

    def args(self):
                
        return self._main_part[1:]
    

    








        

@dataclass
class CommandInvocArgs:
    spec : CommandInvocSpec
    position : Any
    shell_context: Any



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
            
            
        if self._in_new_proc(): 
            
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
        
        with self._error_fd_setup():
            with self.child_fd_setup(in_fd, out_fd):
                self.run_core()                
            
    def _run_in_parent(self, in_fd, out_fd):
        
        def cur_stdout():
            return os.dup(STDOUT)
        
        def set_output_to_fd(out_fd):
            os.dup2(out_fd, STDOUT)
        
        def reset_output_to_stdout(save_stdout):
            os.dup2(save_stdout, STDOUT)
        
        with self._error_fd_setup():
        
            try:
                save_stdout = cur_stdout() 
                set_output_to_fd(out_fd) 
                
                self.run_core()
            
            finally:   
                reset_output_to_stdout(save_stdout)
                    
                
    @contextmanager         
    def _error_fd_setup(self):
        
        @contextmanager
        def redirect_stderr_to_fd(err_file, mode):
            
            STDERR = 2
            
            def new_fd(file, modee):
                if modee == RedirectMode.APPEND:
                    return open_append(file)
                elif modee == RedirectMode.WRITE:
                    return open_write(file)
            
            def cur_stderr():
                return os.dup(STDERR)
                
            def send_err_to_fd(fd):
                os.dup2( fd , STDERR )
                
            def reset_err_to_stderr(save_stderr):
                os.dup2( save_stderr, STDERR) 
                
            def close_fds(error_fd, save_stderr):
                os.close(error_fd)
                os.close(save_stderr)
                
            try:
                error_fd = new_fd(err_file, mode)
                save_stderr = cur_stderr()
                send_err_to_fd(error_fd)
                
                yield
                
            finally:
                reset_err_to_stderr(save_stderr)
                close_fds(error_fd, save_stderr)
                
                
            
        
        if not self.spec().rt_stderr: 
            yield
        
        else:
            
            err_file = self.spec().rt_stderr.file
            mode = self.spec().rt_stderr.mode
            
            with redirect_stderr_to_fd( err_file, mode ) :
                yield
    
    
    def _in_new_proc(self):
        return self.in_pipe() or self._new_proc_in_standalone()
    
    def _file_descriptors(self):
        
        if self.spec().rt_stdout:
            
            out_file = self.spec().rt_stdout.file
            mode = self.spec().rt_stdout.mode
            
            next_in_fd = None
            
            if mode == RedirectMode.APPEND:
                out_fd = open_append( out_file )
            
            elif mode == RedirectMode.WRITE:     
                out_fd = open_write( out_file )       

        elif not self.last_invoc(): #not last invocation -  we need a pipe
            next_in_fd, out_fd = os.pipe()
            
        else: # default values - no next input, output to stdout
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