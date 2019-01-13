from socket import *
import pickle
import argparse
import sys
import time

#takes the port number as command line arguments
IP_ADDRESS = ""
PORT = 8080
FILE_NAME = ""
BUFFER_SIZE = 1472
# Definding key parameters of programm
# it could be port, address, file, buffer_size, window_size or timeout
parser = argparse.ArgumentParser()  # creating key-parser object
parser.add_argument("-p", "--port", type=int, help="specify the server port")
parser.add_argument("-a", "--address", type=str, help="specify the server address")
parser.add_argument("-f", "--file", type=str, help="specify the transieved file")
args = parser.parse_args()

# checking whether parameters was setted
IP_ADDRESS = args.address if args.address else IP_ADDRESS  # set ip address from input parameter else by default
PORT = args.port if args.port else PORT  				   # set port from input parameter else by default


#takes the file name as command line arguments


#create client socket
sock = socket(AF_INET, SOCK_DGRAM)     # set up that socket work via UDP protocol
sock.settimeout(0.01)    # socket timeout after finishing of transmitting
ADDR = (IP_ADDRESS, PORT)

#initializes window variables (upper and lower window bounds, position of next seq number)
base = 1
nextSeqnum = 1
windowSize = 7
window = []

def file_open(name):
    '''
    General purpose function, that give abtraction from a way that file will be opened. If name is given,
    that means, that program started with -f key, else program read data from stdin.
    name -- (str) filename to open, if -f key setted, else use stdin
    return -- (fd / stdin) return function, it does not matter whether this will be fd or stdin because both function have
    read and write methods.
    '''
    if name:
        try:
            return open(name, 'rb') # if name is given as a paramiter returns file descriptor
        except Exception: sys.exit(0)
    else:
        try:
            return sys.stdin       # else returns stdin
        except Exception: sys.exit(0)

# SENDS DATA
fileOpen = file_open(args.file)    # opening file for reading
data = fileOpen.read(BUFFER_SIZE)    # adding data to packets
done = False
lastackreceived = time.time()    # writing the time of last received packet

while not done or window:
    # check if the window is full or EOF has reached
    if(nextSeqnum < base+windowSize) and not done:
        # create packet(seqnum, data)
        sndpkt = []    # creating list
        sndpkt.append(nextSeqnum)
        sndpkt.append(data)
        sock.sendto(pickle.dumps(sndpkt), ADDR)    # send packet
        print("Sent data", nextSeqnum)

        nextSeqnum = nextSeqnum + 1    # increment variable nextSeqnum

        # adding packets to the end of window
        if(not data):
            done = True
        window.append(sndpkt)    # adding packet to window
        data = fileOpen.read(BUFFER_SIZE)    # adding data to packets

#RECEIPT OF AN ACK
    try:
        packet, serverAddress = sock.recvfrom(4096)    # receive packets
        rcvpkt = []
        rcvpkt = pickle.loads(packet)    # assign received data
        print("Received ack for", rcvpkt[0])

        # slide window and reset timer
        while rcvpkt[0] > base and window:
            lastackreceived = time.time()
            del window[0]
            base = base + 1
    # else:
    #     print ("error detected")

#TIMEOUT
    except:
        if time.time()-lastackreceived > 0.01:
            for i in window:
             sock.sendto(pickle.dumps(i), ADDR)

fileOpen.close()    # closing file

print("connection closed")
sock.close()    # closing connection