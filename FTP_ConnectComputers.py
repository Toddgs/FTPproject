import socket
import pickle
import optparse                                         # This is used to parse console input
import string
import os

# import threading                                      # used in server

 

def cd(newDirectory, socket):
    socket.send(pickle.dumps('cd', protocol=2))

def ls(socket):
    socket.send(pickle.dumps('ls', protocol=2))                                                           
    bytesRecv = pickle.loads(socket.recv(1024))                                         
    return bytesRecv

def dir(newDirectory, socket):
    cmd = pickle.dumps('dir', protocol=2)
    socket.send(cmd)                                  
    data = socket.recv(1024)                           
    bytesRecv = pickle.loads(data)                        
    return bytesRecv

def get(command, socket):   
    cmd = pickle.dumps(command,protocol=2)
    socket.send(cmd)
    print ('sent cmd')
    f = open('new_' + command[4:], 'wb')
    data = b''
    while True:                              ##################################################
        packet = socket.recv(1024)
        print('recv1')
        if packet == '': break
        data += packet
        packet = ''
        print ('try for mor')
    print ('exit 1st while')
    message = pickle.loads(data)
    if  message[:5] == "ERROR":
        print(pickle.loads(data))
        return
    while (data != ''):
        print('while')
        f.write(data)
        data = socket.recv(1024)
        print('recv')

def putFile(socket, cmd): #This function needs to put a file from the local machine to the server.
    tempName = cmd[3:]
    
    if os.path.isfile(tempName): #Checks to see if the file exists.
        print('do stuff')
        socket.send(cmd)
        success = socket.recv(1024)
        if success:
            socket.send(os.path.getsize(tempName))
            success = socket.recv(1024)
            if success:
                with open(tempName, 'rb') as f:
                    bytesToSend = f.read(1024)
                    socket.send(bytesToSend)
                    while bytesToSend != '':
                        bytesToSend = f.read(1024)
                        socket.send(bytesToSend)

    else:
        print("ERROR: Filename not valid.")

def multiget(socket):
    cmd = pickle.dumps('mget', protocol=2)
    socket.send(cmd)                                   
    data = socket.recv(1024)                           
    bytesRecv = pickle.loads(data)                                         
    return bytesRecv

def multiput(socket):
    cmd = pickle.dumps('mput',protocol=2)
    socket.send(cmd)                                   
    data = socket.recv(1024)                         
    bytesRecv = pickle.loads(data)                                   
    return bytesRecv
 
def changeDir(socket):
    cmd = pickle.dumps('cd',protocol=2)
    socket.send(cmd)                                  
    data = socket.recv(1024)                          
    bytesRecv = pickle.loads(data)                                         
    return bytesRecv

def quit(socket):
    socket.close()

def Main():#host = input("Enter the IP address of your server: ") # older versions of python will have to use raw_input
    host = "169.254.145.232"                    # Todd's IP address, Personal IP: 10.20.120.61
    port  = 5000                                        # actual port
 
    s = socket.socket()                                 # creates the "port" we use to connect

    s.connect((host,port))                              # This connects to the server
    login = pickle.loads(s.recv(1024))          # Promted by server imedeately after connection
    if login == "LOGIN":
        loginName = input("Please enter username: ")# Prompt to see if account isalreadycreated
        if loginName == "anon":
            loginEmail = input("Please enter your e-mail: ")
            loginInfo = [loginName, loginEmail]
        else:
            password = input("Please enter your password: ")
            loginInfo = [loginName, password]
        data = pickle.dumps(loginInfo, protocol=2)
        s.send(data)
    while True:
        commandInput = input(">")                      

        if commandInput[:2] == "ls":
            lis = ls(s)
            print(lis)

        if commandInput[:2] == "cd":
            newDirectory = input("Name of Directory?")                      
            if newDirectory != 'quit':                             
                directory = cd(newDirectory, s)

        if commandInput[:3] == "dir":
            ls(s)
 
        if commandInput[:3] == "get":
            get(commandInput, s)

        if commandInput[:3] == "put":
            putFile(s)

        if commandInput[:4] == "mget":
            multiget(s)

        if commandInput[:4] == "mput":
            multiput(s)

        if commandInput[:3] == 'lcd':
            dirList = os.listdir(".\\")
            print ('My list:', *dirList, sep='\n')

        if commandInput[:4] == "quit":
            quit(s)
            exit()

if __name__ == '__main__':
    Main()