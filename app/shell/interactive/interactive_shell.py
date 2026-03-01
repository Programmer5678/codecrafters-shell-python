import os
import readline

from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from app.search_files import all_execs_in_path

def gen_completer(cwd):
    
    def result(text: str, state: int) -> str:
        
        def not_first_match():
            return state > 0
        
        def invoc_start():
            last_invoc = readline.get_line_buffer().split("|")[-1].strip()
            return last_invoc.startswith(text)
        
        def complete_command_action():
            
            def remove_dups( l ):
                return list( dict.fromkeys(l) )
            
            all_commands_with_dups = list(BuiltinCommandInvoc.commands().keys()) + [ f.file() for f in all_execs_in_path() ]
            all_commands = remove_dups(all_commands_with_dups)
            matching_commands = [ com for com in all_commands if com.startswith(text) ]  
        
            if len(matching_commands) == 1:
                matching_com = matching_commands[0]
                return matching_com + " "
            else:
                return None
            
        def complete_file_action():
            
            def preceeding_path():
                last_word = readline.get_line_buffer().split()[-1]
                return last_word[ :-len(text) ]
            
            def search_completion_in_dir(dir):
                                
                def is_match(file):
                    return file.startswith(text)
                
                def suffix(file):
                    
                    def is_file():
                        return os.path.isfile( os.path.join(dir, file) )
                    
                    def is_dir():
                        return os.path.isdir( os.path.join(dir, file) )
                    
                    if is_file():
                        return " "
                    elif is_dir():
                        return "/"
                    
                def least_common_prefix(l):
                    
                    def _least_common_prefix(s1, s2):
                        
                        result = ""
                        for c1, c2 in zip(s1,s2): #Loop through strings
                            
                            if c1 == c2:  #this c also belongs in prefix
                                result+=c1 # append c to prefix
                            else:
                                break 
                            
                        return result
                            
                    
                    if len(l) == 1:
                        return l[0]
                    
                    else: 
                        return least_common_prefix( l[:-2] + [ _least_common_prefix( l[-2], l[-1] ) ] )
                    
                def full_completion(match):
                    return match + suffix(match)
                
                def complete_to_common_prefix(matches):
                    
                    def prefix_already_maximal(lcp):
                        return lcp == text
                    
                    lcp = least_common_prefix(matches)
                    
                    if prefix_already_maximal(lcp):
                        return None
                    else:
                        return lcp 
                
                files_in_dir = os.listdir(dir)
                files_in_dir.sort()
                
                matches = [ file for file in files_in_dir if is_match(file) ]
                if len(matches) == 1:
                    match = matches[0]
                    return full_completion(match)
                
                elif len(matches) > 1:
                    return complete_to_common_prefix(matches)
                
                #No matches :(
                return None
                        
            dir_to_search = os.path.join( cwd, preceeding_path() )
            return search_completion_in_dir(dir_to_search)
            

        if not_first_match():
            return None 
                
        if invoc_start():
            return complete_command_action()
            
        else:
            return complete_file_action()
            

                
    return result

# matching_commands = [ com + " " for com in list(BuiltinCommandInvoc.commands().keys()) if com.startswith(text) ]

def setup_interactive_shell():
    readline.parse_and_bind("tab: complete")
    readline.set_completer( gen_completer( os.getcwd() ) )
    readline.set_auto_history(False)
    
def update_cwd_completer(cwd):
    readline.set_completer( gen_completer(cwd) )
    
    