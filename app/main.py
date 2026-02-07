import sys

def main():
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        line = sys.stdin.readline()
        command = line.split()[0]
        words = line.split()[1:]
        
        if command == "exit":
            exit(0)
            
        if command == "echo":
            sys.stdout.write(" ".join(words) + "\n")
            sys.stdout.flush()
            
        else:
            sys.stdout.write(f"{command}: command not found\n")
            sys.stdout.flush()
    


if __name__ == "__main__":
    main()
