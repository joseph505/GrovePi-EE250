import sys
# By appending the folder of all the GrovePi libraries to the system path here,
# we are successfully `from grovepi import *`
sys.path.append('../../Software/Python/')
import grovepi 
import socket

def Main():
    # Change the host and port as needed. For ports, use a number in the 9000 
    # range. 
    host = '192.168.1.217'
    port = 8000

    server_addr = '10.0.2.15'

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    s.bind((host,port))

     # UDP is connectionless, so a client does not formally connect to a server
    # before sending a message.
    dst_port = input("destination port-> ")

    while True:
    	#tuples are immutable so we need to overwrite the last tuple
        server = (server_addr, int(dst_port))
        s.sendto((grovepi.ultrasonicRead(ultrasonic_ranger)).encode('utf-8'), server)
    s.close()


if __name__ == '__main__':
    Main()
#use UDP