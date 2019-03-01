import socket, pickle
import threading
import os

#Will require an input to change directories 
def cd(newDirectory, socket):
    #change directory
    if os.path.isdir(newDirectory):
        os.chdir(newDirectory)

#List all files and directories contained in current working directory
def ls(s):
    #s.send(str.encode(directoryList))
    print("Picklin...")
    data_string = pickle.dumps(os.listdir(".\\")) #we might be able to combine This line with the next one.
    s.send(data_string)
    print("Pickled!")

#Will require an input to change directories
def dir(newDirectory, socket):
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

def login(socket):
    socket.send("LOGIN")
    userName = socket.recv(1024)
    password = socket.recv(1024)
    print("Username: " + userName + " Password: " + password)



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
    c, addr = s.accept()
    
    print("client connected ip:<" + str(addr) + ">")
    login(c)
    
    while True:
        
        cmd = str.decode(c.recv(1024))
        #cmd = cmd.lower
        print(cmd)
        if cmd == 'cd':
            directory = c.recv(1024)
            cd(directory, c)

        elif cmd == 'LS':
            #directory = '' #Current working directory.
            print("Entering LS")
            ls(c)
            print("Returned LS")

        elif cmd == 'GET':
            filename = c.recv(1024)
            get(filename, c)

        elif cmd == 'PUT':
            fileName = c.recv(1024)
            put(fileName, c)

        elif cmd == 'MGET':
            fileNames = c.recv(1024)
            mget(fileNames, c)

        elif cmd == 'MPUT':
            fileName = c.recv(1024)
            mput(fileName, c)

        elif cmd == 'QUIT':
            quit(s) 
        
        #t = threading.Thread(target=RetrFile, args=("retrThread", c))
        #t.start()
    s.close()

if __name__ == '__main__':
    main()