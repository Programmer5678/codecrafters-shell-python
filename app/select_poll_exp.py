import subprocess



file1 = subprocess.Popen( ["tail", "-f", "/tmp/file1.txt"], stdout = subprocess.PIPE, text=True )
file2 = subprocess.Popen( ["tail", "-f", "/tmp/file2.txt"], stdout = subprocess.PIPE, text=True )

streams = {
    file1.stdout.fileno() : ( "file1", file1.stdout ),
    file2.stdout.fileno() : ( "file2", file2.stdout ),
}

while len( streams.keys() ) > 0:
    readable, _, _ = streams.select(streams.keys(), [], [])
    for fd in readable:
        filename, pipe = streams[fd]
        data = pipe.read1( 4096 )
        if not data:
            del streams[fd]
            continue
        
        print( f"{filename}:\n{s}" )
        
        

class Stream:
    
    def __init__(self, out_pipe, err_pipe ):
        self._out_pipe = out_pipe
        self._err_pipe = err_pipe
        
    def print_all():
        
        
