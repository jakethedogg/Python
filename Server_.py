from socket import *
import pickle
import sys
import time
import argparse

#takes the port number as command line arguments and create server socket
IP_ADDRESS = "0.0.0.0"   # accept all incoming client
PORT = 8080    # Port by default
ADDR = None    # initialization of address variable
FILE_NAME = ""   # Initializing filename variable
BUFFER_SIZE = 4096

# Definding key parameters of programm
# it could be port, file, buffer_size, window_size or timeout
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int, help="specify the server port")
parser.add_argument("-f", "--file", type=str, help="specify the transieved file")
args = parser.parse_args()


def file_open(name):
    '''
    General purpose function, that give abtraction from a way that file will be opened. If name is given,
	that means, that program started with -f key, else program read data from stdin.
	:param name: (str) name of file, if -f key setted
	:return: (fd / stdin) return function, it does not matter whether this will be fd or stdin because both function have
	read and write methods.
    '''
    if name:
        try:
            return open(name, 'wb')  # if name is given as a paramiter returns file descriptor
        except Exception:
            sys.exit(0)
    else:
        return sys.stdout  # else returns stdout


serverSocket = socket(AF_INET, SOCK_DGRAM)    # set up that socket work via UDP protocol
serverSocket.bind((IP_ADDRESS, PORT))    # connection between server and client
serverSocket.settimeout(1)    # socket timeout after finishing of transmitting
print("Ready to serve")

#initializes packet variables 
expectedseqnum = 1    # a package header, a 1-cell packet
ACK = 1    # caption
ack = []    # create a list

#RECEIVES DATA
f = file_open(args.file)
endoffile = False
lastpktreceived = time.time()	 # counting time
starttime = None    # write time when the script start working

while True:
    try:
        rcvpkt = []    # empty list
        packet, clientAddress = serverSocket.recvfrom(BUFFER_SIZE)    # receive packates
        rcvpkt = pickle.loads(packet)    # assign received packages to variable
        if starttime == None:
            starttime = time.time()    # write to variable the time
        # check value of expected seq number against seq number received - IN ORDER
        if rcvpkt[0] == expectedseqnum:
            print("Received inorder", expectedseqnum)
            if rcvpkt[1]:    # checking if there some data
                f.write(rcvpkt[1])    # writing the data into the file
            else:
                endoffile = True
            expectedseqnum = expectedseqnum + 1    # growing the header variable
            # create ACK (seqnum,checksum)
            sndpkt = []
            sndpkt.append(expectedseqnum)    # create ack
            serverSocket.sendto(pickle.dumps(sndpkt), clientAddress)    # send ack to the client
            print("New Ack", expectedseqnum)

        else:
            # discard packet and resend ACK for most recently received inorder pkt
            print("Received out of order", rcvpkt[0])
            sndpkt = []
            sndpkt.append(expectedseqnum)
            serverSocket.sendto(pickle.dumps(sndpkt), clientAddress)    # send packets to the client
            print("Ack", expectedseqnum)

    except:
        if endoffile:
            if time.time()-lastpktreceived > 3:
                break



endtime = time.time()
f.close()
print('FILE TRANFER SUCCESSFUL')
print("TIME TAKEN ", str(endtime - starttime))