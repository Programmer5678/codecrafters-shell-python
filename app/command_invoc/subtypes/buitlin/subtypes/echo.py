from app.command_invoc.subtypes.buitlin.builtin import BuiltinCommandInvoc
from multiprocessing import Process
import os

# def runny(w):
#     print( " ".join( self.spec().args() ), stdout=w )

# def runny(w):
#     print( "Mekhaka ul adama khama", stdout=w )


# def wrapper(w):
    
#     runny(w)
#     os.close(w)

class EchoCommand(BuiltinCommandInvoc):

    expected_command="echo"

    def run( self, stdin ):
        pass
        
        # r, w = os.pipe()
        # p = Process(target=runny, args=(w,))
        # p.start()
        
        # os.close(w)
            
        # print(  os.read(r, 1024).decode()  )     
        
        # p.join()   
            