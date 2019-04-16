import socket, pickle
import threading
import os
import zlib
import Cryptodome
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES, PKCS1_OAEP

#Will require an input to change directories 
def cd(newDirectory, socket): #Change directory function.
    if os.path.isdir(newDirectory):
        os.chdir(newDirectory)

def ls(s): #List all files and directories contained in current working directory
    data_string = pickle.dumps(os.listdir(".\\")) #Takes the data and uses the pickle library to serialize it into the data_string variable.
    s.send(data_string) #Sends the serialized data string.

#Will require an input to change directories
def dir(newDirectory, socket):
    if os.path.isdir(newDirectory): #Checks to see if the directory exists
        os.chdir(newDirectory) #Changes to the specified directory if it exists.
    else:
        socket.send("ERROR:Not a directory") #Sends an error message if the directory does not exist.

#Will take an input to retrieve a file. 
def get(name, socket, compress, encrypt):
    if os.path.isfile(name):
        size = pickle.dumps(os.path.getsize(name)) #takes the size of the named file and puts it into a pickled format.
        socket.send(size)
        with open(name, 'rb') as f: #Opens the file with the specified name
            bytesToSend = f.read(1024) #Reads the first section of data to be sent.
            while bytesToSend != b'': #Checks to see if the data is empty
                socket.send(bytesToSend)
                bytesToSend = f.read(1024) #If not, sends more data.
    else:
        print("ERROR MSG")
        errorMsg = pickle.dumps("ERROR:File doesn't exist")
        socket.send(errorMsg) #Sends an error message.
    socket.close #Closes the socket 

def put(cmd, sock, compress, encrypt): #Will prompt for a file to transfer to current working directory.
    zobj = zlib.decompressobj()
    pickleTrue = pickle.dumps(True) #Prepares a true statement to be sent to the client.
    name = cmd[3:] #Pulls the name from the cmd variable.
    filesize = sock.recv(1024)
    filesize = pickle.loads(filesize)
    if filesize: #If filesize exists, enter this statement.
        sock.send(pickleTrue) #Send a confirmation that the statement passed and we entered the if statement.
        f = open('new_' + name, 'wb')        # makes file with the word new infront 
        if compress:
            data = sock.recv(1024)
            decompressedData = zobj.decompress(data)
            totalRecv = len(decompressedData) #Sets the initial value of totalRecv to the size of the first packet. 
            f.write(decompressedData) #Writes the data to the file. 
            while totalRecv < filesize: #If the totalRecv is less than the filesize enter the while loop.
                data = sock.recv(1024) 
                decompressedData = zobj.decompress(data)
                totalRecv += len(decompressedData)
                f.write(decompressedData)

        elif encrypt:
            file_in = open("encrypted_data.bin", "rb")

            private_key = RSA.import_key(open("private.pem").read())

            enc_session_key, nonce, tag, ciphertext = \
            [ file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]

            # Decrypt the session key with the private RSA key
            cipher_rsa = PKCS1_OAEP.new(private_key)
            session_key = cipher_rsa.decrypt(enc_session_key)

            # Decrypt the data with the AES session key
            cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
            data = cipher_aes.decrypt_and_verify(ciphertext, tag)
            print(data.decode("utf-8"))
        
        elif compress & encrypt:
            file_in = open("encrypted_data.bin", "rb")

            private_key = RSA.import_key(open("private.pem").read())

            enc_session_key, nonce, tag, ciphertext = \
            [ file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]

            # Decrypt the session key with the private RSA key
            cipher_rsa = PKCS1_OAEP.new(private_key)
            session_key = cipher_rsa.decrypt(enc_session_key)

            # Decrypt the data with the AES session key
            cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
            data = cipher_aes.decrypt_and_verify(ciphertext, tag)
            print(data.decode("utf-8"))
            
            data = sock.recv(1024)
            decompressedData = zobj.decompress(data)
            totalRecv = len(decompressedData) #Sets the initial value of totalRecv to the size of the first packet. 
            f.write(decompressedData) #Writes the data to the file. 
            while totalRecv < filesize: #If the totalRecv is less than the filesize enter the while loop.
                data = sock.recv(1024) 
                decompressedData = zobj.decompress(data)
                totalRecv += len(decompressedData)
                f.write(decompressedData)
        
        else:
            data = sock.recv(1024)
            totalRecv = len(data) #Sets the initial value of totalRecv to the size of the first packet. 
            f.write(data) #Writes the data to the file. 
            while totalRecv < filesize: #If the totalRecv is less than the filesize enter the while loop.
                data = sock.recv(1024) 
                totalRecv += len(data)
                f.write(data)

#Will allow for multiple gets of several files. Must allow wildcard (*)
def mget(names, socket, compress, encrypt):
    namesDict = names.split() #Seperate out all the names for the files

def mput(names, socket, compress, encrypt): #Will prompt user to send multiple files to the CWD
    namesDict = names.split() #split the names into a dictionary so that we can easily setup the files.
    for name in namesDict: #For every name in the dictionary DO THE THING
        if os.path.isfile(name): #Need to prompt the user about the error with the filename.
            socket.send("ERROR:") #Error message

def quit(socket): #Exits the program and closes the connection.
    socket.send("GOODBYE") #Tell the client that we are closing the connection.
    socket.close #Close the connection.

def login(socket): #Login function, user must login or be booted.
    numberOfTries = 0 #Variable to count the number of attempts.
    login = pickle.dumps("LOGIN")
    socket.send(login) #Tell the client that we are attempting to log in
    data = pickle.loads(socket.recv(1024)) #Open the socket to receive data.
    userData = data #Unload the pickled data. 
    if userData[0] == "" and numberOfTries != 3: #While the number of login attempts is less than 3. 
        socket.send("LOGIN") # THIS FUNCTION NEEDS TO BE UPDATED AND CHANGED TO A WHILE LOOP
        numberOfTries += 1
    elif userData[0] == "" and numberOfTries == 3:
        socket.send("You must login!")
        quit(socket)
        return
    else:
        print("Username: " + userData[0] + " Password: " + userData[1]) #Prints the users login information.

def main(): #Main function.
    compress = False
    encrypt = False
    host = '10.0.0.49' #169.254.145.232' 
    port = 5000
    s = socket.socket() #Create a socket object.
    s.bind((host,port)) #Bind the information to the socket object.
    cmd = ''
    s.listen(5) #A timeout for the listen. Will likely not need this in the final code.
    print("Server Started.")
    c, addr = s.accept() #Waits and accepts outside connections.
    
    print("client connected ip:<" + str(addr) + ">") #Prints the connecting IP address.
    login(c) #Go into the login function. If they fail they will be logged out.
    
    while True:
        cmd = pickle.loads(c.recv(1024)) #Get the cmd data from the client.
        print(cmd) #Prints the command the user entered. 
        if 'enc' in cmd:
            cmd = cmd[4:] #Cut out the encrypt from the command
            encrypt = True #Set the encrypt varialbe to true
        if 'cmp' in cmd:
            cmd = cmd[4:] #Cut out the compress from the command
            compress = True #Set the compress variable to true

        if cmd[:2] == 'cd': 
             cd(cmd[3:], c)

        elif cmd[:2] == 'ls':
            ls(c)

        elif cmd[:3] == 'get':
            print(cmd[4:])
            get(cmd[4:], c, compress, encrypt)

        elif cmd[:3] == 'put':
            print('entering put...')
            put(cmd, c, compress, encrypt)

        elif cmd[:4] == 'mget':
            fileNames = c.recv(1024)
            mget(fileNames, c, compress, encrypt)

        elif cmd[:4] == 'mput':
            fileName = c.recv(1024)
            mput(fileName, c, compress, encrypt)

        

        elif cmd[:4] == 'quit':
            quit(s) 
        
        #t = threading.Thread(target=RetrFile, args=("retrThread", c))
        #t.start()
        print(cmd)
        print('end of loop...')
    s.close()

if __name__ == '__main__':
    main()