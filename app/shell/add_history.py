import readline

def add_history(shell_context, line):
    shell_context.add_line_history( line )
    readline.add_history( line )