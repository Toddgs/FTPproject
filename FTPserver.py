import socket
import threading
import os

#Will require an input to change directories 
def cd(newDirectory):
    #change directory
    if os.path.isdir(newDirectory):
        os.chdir(newDirectory)


#List all files and directories contained in current working directory
def ls(currentDirectory):
    os.listdir(currentDirectory)

#Will require an input to change directories
def dir(newDirectory):
    if os.path.isdir(newDirectory):
        os.chdir(newDirectory)

#Will take an input to retrieve a file. 
def get(name, socket):
    
    if os.path.isfile(str.decode(name)):
        #socket.send('EXISTS' + str(os.path.getsize(filename)))
        #userResponse = socket.recv(1024)
        #if userResponse[:2] == 'OK':
        with open(name, 'rb') as f:
            bytesToSend = f.read(1024)
            socket.send(bytesToSend)
            while bytesToSend != '':
                bytesToSend = f.read(1024)
                socket.send(bytesToSend)
    else:
        socket.send("ERR")
    socket.close


#Will prompt for a file to transfer to current working directory.
def put(name, socket):


#Will allow for multiple gets of several files. Must allow wildcard (*)
def mget():


#Will prompt user to send multiple files to the CWD
def mput():


#exits the program and closes the connection.
def quit(socket):
    socket.send("GOODBYE")
    socket.close


""" def RetrFile(name, socket):
    filename = socket.recv(1024)
    #socket.send(str.decode(filename))
    if os.path.isfile(str.decode(filename)):
        socket.send('EXISTS' + str(os.path.getsize(filename)))
        userResponse = socket.recv(1024)
        if userResponse[:2] == 'OK':
            with open(filename, 'rb') as f:
                bytesToSend = f.read(1024)
                socket.send(bytesToSend)
                while bytesToSend != '':
                    bytesToSend = f.read(1024)
                    socket.send(bytesToSend)
    else:
        socket.send("ERR")
    socket.close """

def main():
    host = '169.254.145.232'
    port = 5000
    s = socket.socket()
    s.bind((host,port))
    cmd = ''
    s.listen(5)

    print("Server Started.")
    while True:
        c, addr = s.accept()
        print("client connected ip:<" + str(addr) + ">")
        cmd = socket.recv(1024)
        
        if str.decode(cmd) == 'CD':
            cd()

        elif str.decode(cmd) == 'LS':
            ls()

        elif str.decode(cmd) == 'GET':
            filename = socket.recv(1024)
            get(name, socket)

        elif str.decode(cmd) == 'PUT':
            put()

        elif str.decode(cmd) == 'MGET':
            mget()

        elif str.decode(cmd) == 'MPUT':
            mput()

        elif str.decode(cmd) == 'QUIT':
            quit() 
        
        t = threading.Thread(target=RetrFile, args=("retrThread", c))
        t.start()
    s.close()

if __name__ == '__main__':
    main()
        
         
