import sys

def invalid(word):
    return True

def main():
    sys.stdout.write("$ ")
    sys.stdout.flush()
    line = sys.stdin.readline()
    firstWord = line.split()[0]
    if invalid(firstWord):
        sys.stdout.write(f"{firstWord}: command not found")
    pass


if __name__ == "__main__":
    main()
