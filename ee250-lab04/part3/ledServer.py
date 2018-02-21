# LED Server
# 
# This program runs on the Raspberry Pi and accepts requests to turn on and off
# the LED via TCP packets.

import sys
# By appending the folder of all the GrovePi libraries to the system path here,
# we are successfully `import grovepi`
sys.path.append('../../Software/Python/')


#UNCOMMENT THIS WHEN ACTUALLY DEPLOYING ON GROVEPI
import grovepi

#Digital port d4 
led = 4 
pinMode(led, "OUTPUT") 

import socket



# use TCP

def Main():
    host = '127.0.0.1' #GrovePi IP Address 
    port = 5000

    s = socket.socket()
    s.bind((host,port))

    s.listen(1)
    c, addr = s.accept()
    print("Connection from: " + str(addr))
    while True:
        data = c.recv(1024).decode('utf-8')
        if not data:
            break
        print("From connected user: " + data)
        data = data.upper()

        #added this - Joseph
        on = "LED ON"
        off = "LED OFF"
        if data == on:
            digitalWrite(led, 1)
            data = data + " inside if statement"
      
        elif data == off:
            digitalWrite(led, 0) 
           data = data + " inside if statement"
        
        print("Sending: " + data)
        c.send(data.encode('utf-8'))
    c.close()

if __name__ == '__main__':
    Main()