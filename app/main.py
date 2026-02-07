import sys
import os 


def main():
    
    while True:
        print("$ ", sep =None )
        line = sys.stdin.readline()
        
        command = line.split()[0]
        args = line.split()[1:]
                
        if command == "exit":
            exit(0)
            
        elif command == "echo":
            for arg in args:
                print( arg, sep = " " )
            
        elif command == "type":
            for arg in args:
                if arg in ["exit", "echo", "type"]:
                    print(arg + " is a shell builtin")
                    
                else: 
                    
                    output = arg + ": not found"
                    
                    path = os.environ.get("PATH")
                    
                    for p in path.split(":"):
                        
                        if os.path.isdir(p):
                            
                            for f in os.listdir(p):
                                
                                f2 = os.path.join(p, f)
                                
                                if f == arg and os.path.isfile( f2 ) and os.access(f2, os.X_OK) : 
                                    output = arg + " is " + f2
                    
                    print(output)
  
        else:
            print(f"{command}: command not found")
    


if __name__ == "__main__":
    main()
