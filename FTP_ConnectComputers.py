import socket
import pickle
import optparse                                         # This is used to parse console input
import string
import os
import time
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
    cmd = pickle.dumps(command,protocol=2) #Pickle and send over the required data, Might be able to combine this line with the next line. 
    socket.send(cmd)
    fileSize = socket.recv(1024)
    fileSize = pickle.loads(fileSize) #Receive and unpickle the filesize data. Might be able to combine this line with the above line to save space.
    f = open('new_' + command[4:], 'wb') #Create/Open file to be written.
    sizeRecv = 0 #Set size received to 0 in preperation for receiving data.
    while sizeRecv < fileSize: #Loop while the filesize is greater than the amount of data received.
        packet = socket.recv(1024)
        sizeRecv += len(packet)
        f.write(packet)
        
def putFile(socket, cmd): #This function needs to put a file from the local machine to the server.
    tempName = cmd[4:]
    if os.path.isfile(tempName): #Checks to see if the file exists.
        print('do stuff') #Check, remove after code functions.
        cmd = pickle.dumps(cmd) #Pickle the command to be sent over and send it. Might be able to combine these 2 lines.
        socket.send(cmd)
        time.sleep(0.1) #Might be able to get rid of this delay
        print(os.path.getsize(tempName)) #Check, remove after code functions
        size = pickle.dumps(os.path.getsize(tempName)) #Pickle and send the data, again, might be able to combine lines.
        socket.send(size)
        print("size sent") #Check
        success = socket.recv(1024) #Receive if it suceeded or not.
        print("Received success") #Check
        if success: #If success is true, continue. Not a great implementation but it works.
            print("entered if") #Check
            with open(tempName, 'rb') as f: #Open the file
                bytesToSend = f.read(1024) #Reads the file to be sent, combine with next?
                socket.send(bytesToSend)
                while bytesToSend != '':
                    bytesToSend = f.read(1024) #Continues to send the file until it's empty, combine with next?
                    socket.send(bytesToSend)

    else:
        print("ERROR: Filename not valid.")

def multiget(cmd, socket):
    names = cmd.split(' ')
    for name in names: #For each listed name perform a get function for that name.
        get('get ' + name, socket)

def multiput(socket):
    #cmd = pickle.dumps('mput',protocol=2)
    socket.send(b'mput')                                   
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
    host = "10.0.0.21"                    # Todd's IP address, Personal IP: 10.20.120.61
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
            putFile(s, commandInput)

        if commandInput[:4] == "mget":
            multiget(commandInput[5:], s)

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