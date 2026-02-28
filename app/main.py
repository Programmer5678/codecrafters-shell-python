import copy
import os 
from typing import List

from app.command_invoc.files.absolute_path import absolute
from app.command_invoc.models import InvocOutcome
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from app.command_invoc.subtypes.exec import ExecCommandInvoc
from app.command_invoc.subtypes.notfound import NotFoundCommandInvoc
from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from app.command_invoc.subtypes.buitlin.subtypes.cd import CdCommand
from app.command_invoc.subtypes.buitlin.subtypes.echo import EchoCommand
from app.command_invoc.subtypes.buitlin.subtypes.exit import ExitCommand
from app.command_invoc.subtypes.buitlin.subtypes.history import HistoryCommand
from app.command_invoc.subtypes.buitlin.subtypes.pwd import PwdCommand
from app.command_invoc.subtypes.buitlin.subtypes.type import TypeCommand

from app.command_line import input_lines
from app.shell import add_history, setup_interactive_shell, ShellContext
from app.search_files import all_execs_in_path


class ProcWaiter:
    def __init__(self):
        self._waiter_funcs = []
        
    def add_waiter(self, waiter):
        self._waiter_funcs.append(waiter)
        
    def wait_for_all(self):
        
        for waiter in self._waiter_funcs:
            waiter()
     
                 
     
class CommandInvocIter:
    
    def __init__(self):
        STDIN = 0
        
        self.next_stdin = STDIN
        self.proc_waiter = ProcWaiter()
        self.next_line_shell_context = None
        
    def next_state(self, command_invoc):
        
        result = copy.deepcopy(self)
        
        invoc_outcome = command_invoc.run(result.next_stdin)
        result.next_stdin = invoc_outcome.next_stdin()
        result.proc_waiter.add_waiter(  invoc_outcome.wait_child_end() ) 
        result.next_line_shell_context = invoc_outcome.next_line_shell_context()
            
        return result
      
      
def setup_history():
    
    def get_lines(file):
        with open(file, "r") as f:
            return [ line_full.strip() for line_full in f.readlines() ] 
       
    hist_file = absolute( os.environ.get("HISTFILE", "~/.bash_history"), os.getcwd() )
        
        
    if not os.path.exists(hist_file):
        return []
    else:
        return get_lines(hist_file)
    
def save_history(shell_context):
    history_lines = shell_context.session_history()
    history_content = "\n".join( history_lines ) + "\n"
    
    hist_file = absolute( os.environ.get("HISTFILE", "~/.bash_history"), os.getcwd() )
    with open(hist_file, "a+") as f:
        f.write(history_content)
            
def main():
    
    start_history = setup_history()
    setup_interactive_shell()
    shell_context = ShellContext( os.getcwd(), start_history )
    
    try:
    
        for line in input_lines():
                    
            add_history(shell_context, line.raw)
                    
            state = CommandInvocIter()                            
            for command_invoc in line.invocs(shell_context):
                state = state.next_state(command_invoc)
                                
            state.proc_waiter.wait_for_all()
                        
            
            if not state.next_line_shell_context.should_keep_previous():
                shell_context = copy.deepcopy(state.next_line_shell_context.value())
                
    finally:
        save_history(shell_context)
  
                
if __name__ == "__main__":
    main()