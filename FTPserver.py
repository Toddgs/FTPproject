import socket
import threading
import os

#Will require an input to change directories 
def cd(newDirectory, socket):
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
    #What happens if the file exists?
    if os.path.isfile(str.decode(name)):
        null = name
        #Need to prompt the user to change the name or cancel upload
        #After we inform them that a file with that name already exists.
    else:
        null = name
        #Need to go ahead and save the file from the user.

#Will allow for multiple gets of several files. Must allow wildcard (*)
def mget(names, socket):
    #Seperate out all the names for the files
    namesDict = names.split()


#Will prompt user to send multiple files to the CWD
def mput(names, socket):
    namesDict = names.split()
    for name in namesDict:
        if os.path.isfile(name):
            #Need to prompt the user about the error with the filename.
            socket.send("ERR")



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
        cmd = s.recv(1024)
        
        if str.decode(cmd) == 'CD':
            directory = s.recv(1024)
            cd(directory, s)

        elif str.decode(cmd) == 'LS':
            directory = '' #Current working directory.
            ls(directory)

        elif str.decode(cmd) == 'GET':
            filename = s.recv(1024)
            get(filename, socket)

        elif str.decode(cmd) == 'PUT':
            fileName = s.recv(1024)
            put(fileName, s)

        elif str.decode(cmd) == 'MGET':
            fileNames = s.recv(1024)
            mget(fileNames, s)

        elif str.decode(cmd) == 'MPUT':
            fileName = s.recv(1024)
            mput(fileName, s)

        elif str.decode(cmd) == 'QUIT':
            quit(s) 
        
        #t = threading.Thread(target=RetrFile, args=("retrThread", c))
        #t.start()
    s.close()

if __name__ == '__main__':
    main()
        
         
