import readline

from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from app.search_files import all_execs_in_path


def completer(text: str, state: int) -> str:
     
    def not_first_match():
        return state > 0

    if not_first_match():
        return None
     
    all_commands = list(BuiltinCommandInvoc.commands().keys()) + [ f.file() for f in all_execs_in_path() ]
    matching_commands = [ com + " " for com in all_commands if com.startswith(text) ]  

    matching_com = matching_commands[0]
    return matching_com

# matching_commands = [ com + " " for com in list(BuiltinCommandInvoc.commands().keys()) if com.startswith(text) ]

def setup_interactive_shell():
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)
    readline.set_auto_history(False)
    
    