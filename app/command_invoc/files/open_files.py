import os

def open_write(file):
    return os.open(file, os.O_RDWR | os.O_CREAT )

def open_append(file):
    return os.open(file, os.O_RDWR | os.O_CREAT | os.O_APPEND  )