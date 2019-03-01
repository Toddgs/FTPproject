import socket 
import pickle
import optparse #This is used to parse console input -TS
# import threading                                      # used in server 
# get input from user 

#def cd(newDirectory, socket):


def ls(socket):
    socket.send(str.encode('LS'))                       # sends the requested command in bytes
    data = socket.recv(1024)
    bytesRecv = pickle.loads(data)
         
    print('Recv')
    return bytesRecv

def dir(newDirectory, socket):
    socket.send(str.encode('LS'))                       # sends the requested file name in bytes
    dirc = socket.recv(1024)                            # accepts anything sent by server 
    return dirc.decode('utf-8') 

def get(socket):                                        
    filename = input("filename?")                       # gets file desired from client
    if filename != 'quit':                              # 'q' is the indication that the client would like to quit and no longer get a file
        socket.send(str.encode(filename))               # sends the requested file name in bytes
        data = socket.recv(1024)                        # accepts anything sent by server         low key limited to 1018 size file       
        data = data.decode('utf-8')                     # special decode from the string 
        if data[:6] == 'EXISTS':
            filesize = data[6:]
            message = input("File exists, " + filesize + "Bytes, download? (Y/N)")
            if message == 'Y':                          # do a more specific check to verify that the user is saying yes i.e Y, y, yes, Yes, etc.
                socket.send(str.encode('OK'))           # sends back string response
                f = open('new' + filename, 'wb')        # makes file with the word new infront 
                data = socket.recv(1024)
                totalRecv =len(data)
                f.write(data)
                while totalRecv < int(filesize):
                    data = set.recv(1024)
                    totalRecv += len(data)
                    f.write(data)
                    print ("{0:.2f}".format((totalRecv/float(filesize))*100+"% Done"))
                print ("Download Complete!") 
        else:
            print ("File does not Exist!")
    elif filename == 'quit':                            # enters into disconnecting sequence
        socket.send('QUIT')
        quit(socket)

def put(socket):
    print("PUT!")


def mget(socket):
    print("MGET!")

def mput(socket):
    print("MPUT!")

def cd(socket):
    print("CD!")

def quit(socket):
    socket.close()



def Main():
    #host = input("Enter the IP address of your server: ")
    host = "169.254.145.232"                            # Todd's IP address, Personal IP: 10.20.120.61
    port  = 5000                                        # actual port 

    s = socket.socket()                                 # creates the "port" we use to connect
                             # This connects to the server
    
    


    s.connect((host,port))     
    while True:
        cmd = input()
        if cmd.lower == "ls":
            lis = ls(s)
            print(lis)

        if cmd.lower == "get":
            get(s)

        if cmd.lower == "cd":
            cd(s)
        
        if cmd.lower == "dir":
            ls(s)

        if cmd.lower == "get":
            get(s)

        if cmd.lower == "put":
            put(s)

        if cmd.lower == "mget":
            mget(s)
        
        if cmd.lower == "mput": 
            mput(s)

        if cmd.lower == "quit":
            quit(s)
    


if __name__ == '__main__':
    Main()