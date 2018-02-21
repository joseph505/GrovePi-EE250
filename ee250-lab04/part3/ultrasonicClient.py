# Ultrasonic Sensor Client
# 
# This code runs on the Raspberry Pi. It should sit in a loop which reads from
# the Grove Ultrasonic Ranger and sends the reading to the Ultrasonic Sensor 
# Server running on your VM via UDP packets. 

import sys
# By appending the folder of all the GrovePi libraries to the system path here,
# we are able to successfully `import grovepi`
sys.path.append('../../Software/Python/')

import grovepi
import socket

ultrasonic_ranger = 4


def Main():
    # Change the host and port as needed. For ports, use a number in the 9000 
    # range. 
    host = '10.0.2.15' #rpi IP Address 
    port = 1023    

    server_addr = '192.168.1.133' #host OS ip address

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    s.bind((host,port))

    # UDP is connectionless, so a client does not formally connect to a server
    # before sending a message.
    dst_port = input("destination port-> ")
    server = (server_addr, int(dst_port))
    while True:
        # for UDP, sendto() and recvfrom() are used instead
        s.sendto(grovepi.ultrasonicRead(ultrasonic_ranger), server) 
