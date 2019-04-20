import socket
import pickle #Used to store and transfer different data types. 
import optparse                                                                 # This is used to parse console input
import string
import os #Used to get information from the OS
import time
import zlib #Used in Compression
import Cryptodome #Used for encryption (NOT INCLUDED IN THE STANDARD LIBRARY)
import getpass #Used to hide console input for the password.
from Cryptodome.PublicKey import RSA #RSA is an encryption algorithm.
from Cryptodome.Random import get_random_bytes #occasionally you need random bytes for stuff related to encryption.
from Cryptodome.Cipher import AES, PKCS1_OAEP #Advanced Encryption Standard stuff
#import threading                                                               # used in server

def cd(command, socket):                            
    socket.send(pickle.dumps(command, protocol=2))

def ls(socket):
    socket.send(pickle.dumps('ls', protocol=2))                                                           
    bytesRecv = pickle.loads(socket.recv(1024))                                         
    return bytesRecv                                                            #Returns the list to the main

def dir(socket):
    cmd = pickle.dumps('dir', protocol=2)
    socket.send(cmd)                                  
    data = socket.recv(1024)                           
    bytesRecv = pickle.loads(data)                        
    return bytesRecv                                                            #Returns the directory 

def get(command, socket, compress, encrypt):   
    cmd = pickle.dumps(command, protocol=2)                                     #Pickle and send over the required data, Might be able to combine this line with the next line. 
    socket.send(cmd)
    fileSize = socket.recv(1024)
    fileSize = pickle.loads(fileSize)                                           #Receive and unpickle the filesize data. Might be able to combine this line with the above line to save space.
    f = open('new_' + command[4:], 'wb')                                        #Create/Open file to be written.
    sizeRecv = 0                                                                #Set size received to 0 in preperation for receiving data.
    while sizeRecv < fileSize:                                                  #Loop while the filesize is greater than the amount of data received.
        packet = socket.recv(1024)
        sizeRecv += len(packet)
        f.write(packet)
        
def putFile(socket, cmd, compress, encrypt):                                                       #This function needs to put a file from the local machine to the server.
    tempName = cmd[4:]
    zobj = zlib.compressobj()
    if os.path.isfile(tempName):                                                #Checks to see if the file exists.
        if encrypt:
            cmd = "enc " + cmd
        if compress:
            cmd = "cmp " + cmd                      
        cmd = pickle.dumps(cmd)                                                 #Pickle the command to be sent over and send it. Might be able to combine these 2 lines.
        socket.send(cmd)
        time.sleep(0.1)                                                         #Might be able to get rid of this delay
        size = pickle.dumps(os.path.getsize(tempName))                          #Pickle and send the data, again, might be able to combine lines.
        socket.send(size)
        success = socket.recv(1024)                                             #Receive if it suceeded or not.
        if success:                                                             #If success is true, continue. Not a great implementation but it works.
            with open(tempName, 'rb') as f:                                     #Open the file
                if compress:
                    bytesToSend = f.read(1024)                                      #Reads the file to be sent, combine with next?
                    compressedBytes = zobj.compress(bytesToSend)
                    socket.send(compressedBytes)
                    sizeSent = len(bytesToSend)
                    while sizeSent < os.path.getsize(tempName):
                        bytesToSend = f.read(1024)                                  #Continues to send the file until it's empty, combine with next?
                        compressedBytes = zobj.compress(bytesToSend)
                        socket.send(compressedBytes)
                        sizeSent += len(bytesToSend)
                    
                elif encrypt:
                    private_key = RSA.import_key(open("private.pem").read()) #Reads in the private key.
                    session_key = get_random_bytes(16) #Gets some random numbers.
                    cipher_rsa = PKCS1_OAEP.new(private_key) #Encrypt the session key with the private key
                    enc_session_key = cipher_rsa.encrypt(session_key) #Encrypt the session key
                    cipher_aes = AES.new(session_key, AES.MODE_EAX) #Encrypt the session data. 
                    #ciphertext, tag = cipher_aes.encrypt_and_digest(data)
                    #[ file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]
                
                #elif compress & encrypt:
                
                else:
                    bytesToSend = f.read(1024)                                      #Reads the file to be sent, combine with next?
                    socket.send(bytesToSend)
                    sizeSent = len(bytesToSend)
                    while sizeSent < os.path.getsize(tempName):
                        bytesToSend = f.read(1024)                                  #Continues to send the file until it's empty, combine with next?
                        socket.send(bytesToSend)
                        sizeSent += len(bytesToSend)
                    

    else:
        print("ERROR: " + tempName + " not valid.")
    
def multiget(cmd, socket, compress, encrypt):
    print(cmd)
    if '*.*' in cmd: #Checks to find specific command
        fileList = ls(socket) #If found gets every file from the server in the current directory.  
        for name in fileList:
            if '.' in name[1:]: #Hidden directories start with a '.', this ensures we don't try and get directories.
                get('get ' + name, socket, compress, encrypt)

    elif '*.' in cmd:
        fileList = ls(socket) #A list of every file in the current directory.
        for name in fileList: #Check every name in the file list
            if cmd[1:] in name:
                get('get ' + name, socket, compress, encrypt)
                
    elif '.*' in cmd:
        fileList = ls(socket) #A list of every file in the current directory.
        for name in fileList: #Check every name in the file list
            if cmd[:-2] in name:
                get('get ' + name, socket, compress, encrypt)
        
    else:
        names = cmd.split(' ')
        for name in names:                                                          #For each listed name perform a get function for that name.
            if name != ' ':
                get('get ' + name, socket, compress, encrypt)

def multiput(cmd, socket, compress, encrypt):
    command = cmd[5:]
    names = command.split(' ')
    for name in names:                                                          #For each listed name perform a get function for that name.
        if name != ' ':
            putFile(socket, 'put ' + name, compress, encrypt)

def quit(socket):
    socket.close()

def Main():
    #host = input("Enter the IP address of your server: ")                      #older versions of python will have to use raw_input
    host = "10.0.0.49"                                                      # Todd's IP address: 10.20.120.124 Wireless, Personal IP: 10.20.120.61 Wired 
    port  = 5000                                                                # actual port
    encrypt = False
    compress = False

    s = socket.socket()                                                         # creates the "port" we use to connect

    s.connect((host,port))                                                      # This connects to the server
    login = pickle.loads(s.recv(1024))                                          # Promted by server imedeately after connection
    if login == "LOGIN":
        loginName = input("Please enter username: ")                            # Prompt to see if account isalreadycreated
        if loginName == "anon":
            loginEmail = input("Please enter your e-mail: ")
            loginInfo = [loginName, loginEmail]
        else:
            password = getpass.win_getpass("Please enter your password: ")
            loginInfo = [loginName, password]
        data = pickle.dumps(loginInfo, protocol=2)
        s.send(data)
    while True:
        commandInput = input(">")                      

        if commandInput[:2] == "ls":
            lis = ls(s)
            lis.sort()
            print(lis)

        if commandInput[:2] == "cd":                           
            cd(commandInput, s)
            print(ls(s))

        if commandInput[:3] == "dir":
            print(ls(s))
 
        if commandInput[:3] == "get":
            get(commandInput, s, compress, encrypt)

        if commandInput[:3] == "put":
            putFile(s, commandInput, compress, encrypt)

        if commandInput[:4] == "mget":
            multiget(commandInput[5:], s, compress, encrypt)

        if commandInput[:4] == "mput":
            multiput(commandInput, s, compress, encrypt)

        if commandInput[:3] == 'lcd':
            dirList = os.listdir(".\\")
            print ('My list:', *dirList, sep='\n')

        if commandInput == 'encrypt':
            encrypt = True

        if commandInput == 'compress':
            compress = True
        
        if commandInput == 'normal':
            encrypt = False
            compress = False

        if commandInput[:4] == "quit":
            quit(s)
            os._exit(1) #threw error

if __name__ == '__main__':
    Main()
