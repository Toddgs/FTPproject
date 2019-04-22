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

        with open(name, 'rb') as f: #Opens the file with the specified name
            if encrypt:
                clearData = f.read()
                private_key = RSA.import_key(open("private.pem").read()) #Reads in the private key.
                session_key = get_random_bytes(16) #Gets some random numbers.
                cipher_rsa = PKCS1_OAEP.new(private_key) #Encrypt the session key with the private key
                enc_session_key = cipher_rsa.encrypt(session_key) #Encrypt the session key
                cipher_aes = AES.new(session_key, AES.MODE_EAX) #Encrypt the session data. 
                ciphertext, tag = cipher_aes.encrypt_and_digest(clearData)
                temp_Encrypt_File = open('tempFile', 'wb')
                [ temp_Encrypt_File.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]

                size = pickle.dumps(os.path.getsize(temp_Encrypt_File)) #takes the size of the named file and puts it into a pickled format.
                socket.send(size)
                bytesToSend = temp_Encrypt_File.read(1024) #Reads the first section of data to be sent.
                while bytesToSend != b'': #Checks to see if the data is empty
                    socket.send(bytesToSend)
                    bytesToSend = temp_Encrypt_File.read(1024) #If not, sends more data.

                os.remove('tempFile')
            
            elif compress:
                zobj = zlib.compressobj()
                bytesToSend = f.read(1024)                                      #Reads the file to be sent, combine with next?
                compressedBytes = zobj.compress(bytesToSend)
                socket.send(compressedBytes)
                sizeSent = len(bytesToSend)
                while sizeSent < os.path.getsize(name):
                    bytesToSend = f.read(1024)                                  #Continues to send the file until it's empty, combine with next?
                    compressedBytes = zobj.compress(bytesToSend)
                    socket.send(compressedBytes)
                    sizeSent += len(bytesToSend)

            elif encrypt & compress:
                clearData = f.read()
                private_key = RSA.import_key(open("private.pem").read()) #Reads in the private key.
                session_key = get_random_bytes(16) #Gets some random numbers.
                cipher_rsa = PKCS1_OAEP.new(private_key) #Encrypt the session key with the private key
                enc_session_key = cipher_rsa.encrypt(session_key) #Encrypt the session key
                cipher_aes = AES.new(session_key, AES.MODE_EAX) #Encrypt the session data. 
                ciphertext, tag = cipher_aes.encrypt_and_digest(clearData)
                temp_Encrypt_File = open('tempFile', 'wb')
                [ temp_Encrypt_File.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]

                zobj = zlib.compressobj()
                temp_Compress_File = open('tempCompressFile', 'wb')
                temp_Compress_File.write(zobj.compress(temp_Encrypt_File.read()))

                size = pickle.dumps(os.path.getsize(temp_Compress_File)) #takes the size of the named file and puts it into a pickled format.
                
                bytesToSend = temp_Compress_File.read(1024)                                      #Reads the file to be sent, combine with next?
                #compressedBytes = zobj.compress(bytesToSend)
                socket.send(bytesToSend)
                sizeSent = len(bytesToSend)
                while sizeSent < os.path.getsize(temp_Compress_File):
                    bytesToSend = temp_Compress_File.read(1024)                                  #Continues to send the file until it's empty, combine with next?
                    #compressedBytes = zobj.compress(bytesToSend)
                    socket.send(bytesToSend)
                    sizeSent += len(bytesToSend)
                os.remove('tempFile')
                os.remove('tempCompressFile')

            else:
                size = pickle.dumps(os.path.getsize(name)) #takes the size of the named file and puts it into a pickled format.
                socket.send(size)
                bytesToSend = f.read(1024) #Reads the first section of data to be sent.
                while bytesToSend != b'': #Checks to see if the data is empty
                    socket.send(bytesToSend)
                    bytesToSend = f.read(1024) #If not, sends more data.
    else:
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
    #s.listen(5) #A timeout for the listen. Will likely not need this in the final code.
    c, addr = s.accept() #Waits and accepts outside connections.
    login(c) #Go into the login function. If they fail they will be logged out.
    
    while True:
        cmd = pickle.loads(c.recv(1024)) #Get the cmd data from the client.
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
            get(cmd[4:], c, compress, encrypt)

        elif cmd[:3] == 'put':
            put(cmd, c, compress, encrypt)

        elif cmd[:4] == 'quit':
            quit(s) 

if __name__ == '__main__':
    main()