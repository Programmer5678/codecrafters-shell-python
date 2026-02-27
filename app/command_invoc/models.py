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




class FutureShellContext:

    def __init__(self, value, keep=False):
        self._value = value
        self._keep = keep

    @classmethod
    def keep_previous(cls):
        return cls(None, keep=True)

    @classmethod
    def new(cls, value):
        return cls(value, keep=False)

    def should_keep_previous(self):
        return self._keep

    def value(self):
        return self._value

    
        

class InvocOutcome:

    def __init__(self, next_stdin, child_wait, future_shell_context):
        self._next_stdin = next_stdin
        self._child_wait = child_wait
        self._future_shell_context = future_shell_context
        
    @classmethod
    def no_pipeline(cls):
        return cls(None, lambda : None, FutureShellContext.keep_previous() ) 
        
    def next_stdin(self):
        return self._next_stdin
    
    def wait_child_end(self):
        return self._child_wait
    
    def future_shell_context(self):
        return self._future_shell_context





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

            rt_stdout = None
            rt_stderr = None
            
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
                
                def out_file():
                    
                    nonlocal tokens
                    nonlocal index
                    
                    next_token = tokens[index + 1]
                    skip_redirect_iter()
                    return next_token
                    
                def err_file():
                    
                    nonlocal tokens
                    nonlocal index
                    
                    next_token = tokens[index + 1]
                    skip_redirect_iter()
                    return next_token
                
                def is_stderr_redirect(c):
                    return c == "2>"
                
                def is_stderr_append(c):
                    return c == "2>>"
                
                if is_stdout_redirect(cur):
                    rt_stdout = RedirectTarget( out_file() , RedirectMode.WRITE)
                    
                elif is_stdout_append(cur):
                    rt_stdout = RedirectTarget( out_file() , RedirectMode.APPEND)
             
                elif is_stderr_redirect(cur):
                    rt_stderr = RedirectTarget( err_file() , RedirectMode.WRITE)
                    
                elif is_stderr_append(cur):
                    rt_stderr = RedirectTarget( err_file() , RedirectMode.APPEND)
                    
                else:
                    main.append( cur )
                    
                    def advance_loop():
                        nonlocal index
                        index += 1
                        
                    advance_loop()
                                
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
        self.future_shell_context = None

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
        err_fd = self._error_fd()
        future_shell_context = FutureShellContext.keep_previous()
            
        if self._should_spawn_process(): 
            
            """Set up the pipe, spawn child, and return a InvocOutcome."""
            
            child_pid = os.fork()
            in_child_proc = (child_pid == 0)
            if in_child_proc: # if child
                #Run in child
                self._run_in_child(in_fd, out_fd, err_fd) 
                
            else:
            
                self._parent_close_fds(in_fd, out_fd, err_fd)
                wait_child_close = lambda: os.waitpid(child_pid, 0) # Wait func - wait for child to close
                        
        else:
                       
            updated_ctx = self._run_in_parent(in_fd, out_fd, err_fd).updated_end_shell_context()
            
            if updated_ctx.is_update():
                future_shell_context = FutureShellContext.new( updated_ctx.value() )
                
            nothing_func = lambda : None
            wait_child_close = nothing_func

        return InvocOutcome(next_in_fd, wait_child_close, future_shell_context)
    
    def _run_in_child(self, in_fd, out_fd, err_fd):
        
        with self._error_fd_setup(err_fd):
            with self.child_fd_setup(in_fd, out_fd):
                runner = self.run_core()  
                runner.start()              
            
    def _run_in_parent(self, in_fd, out_fd, err_fd):
        
        def cur_stdout():
            return os.dup(STDOUT)
        
        def set_output_to_fd(out_fd):
            os.dup2(out_fd, STDOUT)
        
        def reset_output_to_stdout(save_stdout):
            os.dup2(save_stdout, STDOUT)
        
        with self._error_fd_setup(err_fd):
        
            try:
                save_stdout = cur_stdout() 
                set_output_to_fd(out_fd) 
                
                runner = self.run_core()
                runner.start()
                return runner
                
            
            finally:   
                reset_output_to_stdout(save_stdout)
                    
       
    def _error_fd(self):
        
        STDERR = 2
    
        if self.spec().rt_stderr:
            
            mode = self.spec().rt_stderr.mode
            file = self.spec().rt_stderr.file

            if mode == RedirectMode.APPEND:
                return open_append(file)
            elif mode == RedirectMode.WRITE:
                return open_write(file)
            
        else:
            return STDERR
        
    @contextmanager         
    def _error_fd_setup(self, fd):
        
        STDERR = 2
        
        def cur_stderr():
            return os.dup(STDERR)
            
        def send_err_to_fd(fd):
            os.dup2( fd , STDERR )
            
        def reset_err_to_stderr(save_stderr):
            os.dup2( save_stderr, STDERR) 
            
        def close_fds(error_fd, save_stderr):
            os.close(error_fd)
            os.close(save_stderr)
                
        if fd == STDERR:
            yield
            
        else:
        
            try:
                save_stderr = cur_stderr()
                send_err_to_fd(fd)
                
                yield
                
            finally:
                reset_err_to_stderr(save_stderr)
                close_fds(fd, save_stderr)
             
            
    
    
    def _should_spawn_process(self):
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
    
    @abstractmethod
    @contextmanager
    def child_fd_setup(self, in_fd, out_fd):
        pass
    
    

    def _parent_close_fds(self, in_fd, out_fd, err_fd):
        """Close file descriptors the parent does not need."""
        
        STDERR = 2
        
        if out_fd != STDOUT:
            os.close(out_fd)
        if in_fd is not None and in_fd != STDIN:
            os.close(in_fd)
        if err_fd != STDERR:
            os.close(err_fd)
        
    

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