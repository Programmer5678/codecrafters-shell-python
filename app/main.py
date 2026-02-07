import sys

def invalid(word):
    return True

def main():
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        line = sys.stdin.readline()
        firstWord = line.split()[0]
        
        if firstWord == "exit":
            exit(0)
            
        if invalid(firstWord):
            sys.stdout.write(f"{firstWord}: command not found\n")
    


if __name__ == "__main__":
    main()
