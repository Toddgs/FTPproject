import socket, pickle
import threading
import os

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
        socket.send("ERROR:Not a diretory") #Sends an error message if the directory does not exist.

#Will take an input to retrieve a file. 
def get(name, socket):
    print os.path.isfile(name)
    if os.path.isfile(name):
        with open(name, 'rb') as f: #Opens the file with the specified name
            bytesToSend = f.read(1024) #Reads the first section of data to be sent.
            socket.send(bytesToSend) #Sends the data.
            print "Entering Loop to send"
            while bytesToSend != '': #Checks to see if the data is empty
                bytesToSend = f.read(1024) #If not, sends more data.
                socket.send(bytesToSend)
                print "loopin"
            print "exited loop!"
    else:
        print "ERROR MSG"
        errorMsg = pickle.dumps("ERROR:File doesn't exist")
        socket.send(errorMsg) #Sends an error message.
    socket.close #Closes the socket 

def put(name, socket): #Will prompt for a file to transfer to current working directory.
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
    namesDict = names.split() #Seperate out all the names for the files

def mput(names, socket): #Will prompt user to send multiple files to the CWD
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
    host = '10.0.0.30' #169.254.145.232' 
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
        
        if cmd[:2] == 'cd':
            directory = c.recv(1024) 
            cd(directory, c)

        elif cmd[:2] == 'ls':
            #directory = '' #Current working directory.
            #print("Entering LS")
            ls(c)
            #print("Returned LS")

        elif cmd[:3] == 'get':
            #filename = c.recv(1024)
            print cmd[4:]
            get(cmd[4:], c)

        elif cmd[:3] == 'put':
            fileName = c.recv(1024)
            put(fileName, c)

        elif cmd[:4] == 'mget':
            fileNames = c.recv(1024)
            mget(fileNames, c)

        elif cmd[:4] == 'mput':
            fileName = c.recv(1024)
            mput(fileName, c)

        

        elif cmd[:4] == 'quit':
            quit(s) 
        
        #t = threading.Thread(target=RetrFile, args=("retrThread", c))
        #t.start()
    s.close()

if __name__ == '__main__':
    main()