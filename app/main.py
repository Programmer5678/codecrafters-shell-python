import sys

def main():
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        line = sys.stdin.readline()
        command = line.split()[0]
        words = line.split()[1:]
        
        # sys.stdout.write("COMMAND: " + command + ", WORDS: " + ", ".join(words) + "\n")
        
        if command == "exit":
            exit(0)
            
        elif command == "echo":
            sys.stdout.write(" ".join(words) + "\n")
            sys.stdout.flush()
            
        elif command == "type":
            for arg in words:
                if arg in ["exit", "echo", "type"]:
                    sys.stdout.write(arg + " is a shell builtin\n")
                    sys.stdout.flush()
                    
                else:
                    sys.stdout.write(arg + ": not found\n")
                    sys.stdout.flush()
            
        else:
            sys.stdout.write(f"{command}: command not found\n")
            sys.stdout.flush()
    


if __name__ == "__main__":
    main()
