import sys
import os 

def main():
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        line = sys.stdin.readline()
        command = line.split()[0]
        words = line.split()[1:]
                
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
                    
                    
                    output = arg + ": not found\n"
                    
                    
                    
                    path = os.environ.get("PATH")
                    
                    for p in path.split(":"):
                        
                        if os.path.isdir(p):
                            
                            for f in os.listdir(p):
                                
                                f2 = os.path.join(p, f)
                                
                                if f == arg and os.path.isfile( f2 ) and os.access(f2, os.X_OK) : 
                                    output = arg + " is " + f2 + "\n"
                    
                    sys.stdout.write(output)
                    sys.stdout.flush()
            
        else:
            sys.stdout.write(f"{command}: command not found\n")
            sys.stdout.flush()
    


if __name__ == "__main__":
    main()
