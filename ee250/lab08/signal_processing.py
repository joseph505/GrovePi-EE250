import paho.mqtt.client as mqtt
import time
import requests
import json
from datetime import datetime

# MQTT variables
broker_hostname = "eclipse.usc.edu"
broker_port = 11000
ultrasonic_ranger1_topic = "ultrasonic_ranger1"
ultrasonic_ranger2_topic = "ultrasonic_ranger2"

# Lists holding the ultrasonic ranger sensor distance readings. Change the 
# value of MAX_LIST_LENGTH depending on how many distance samples you would 
# like to keep at any point in time.
MAX_LIST_LENGTH = 10
ranger1_dist = []
ranger2_dist = []

# 2 more buffers for averages
ranger1_dist_avg = []
ranger2_dist_avg = []

# the threshold for determining if people are standing still
threshold = 3

# Global variable for Payload
# The payload of our message starts as a simple dictionary. Before sending
# the HTTP message, we will format this into a json object
# payload = {
#     'time': ,
#     'event':
# }

def ranger1_callback(client, userdata, msg):
    global ranger1_dist
    if(int(msg.payload) > 120):
        msg.payload = "120"

    ranger1_dist.append(int(msg.payload))
    #truncate list to only have the last MAX_LIST_LENGTH values
    ranger1_dist = ranger1_dist[-MAX_LIST_LENGTH:]

    # calculate the average and append to the average list
    rng1 = 0
    for i in range(0, 10):              # sum the data
        rng1 = rng1 + ranger1_dist[i]
    rng1 = rng1 / 10                    # divide by 10 (num of data)
    ranger1_dist_avg.append(rng1)       # append to array
    del ranger1_dist_avg[0]             # delete the first index of the array


def ranger2_callback(client, userdata, msg):
    global ranger2_dist
    if(int(msg.payload) > 120):
        msg.payload = "120"

    ranger2_dist.append(int(msg.payload))
    #truncate list to only have the last MAX_LIST_LENGTH values
    ranger2_dist = ranger2_dist[-MAX_LIST_LENGTH:]

    # calculate the average and append to the average list 
    rng2 = 0
    for i in range(0, 10):              # sum the data
        rng2 = rng2 + ranger2_dist[i]
    rng2 = rng2 / 10                    # divide by 10 (num of data)
    ranger2_dist_avg.append(rng2)       # append to array
    del ranger2_dist_avg[0]             # delete the first index of the array

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(ultrasonic_ranger1_topic)
    client.message_callback_add(ultrasonic_ranger1_topic, ranger1_callback)
    client.subscribe(ultrasonic_ranger2_topic)
    client.message_callback_add(ultrasonic_ranger2_topic, ranger2_callback)

# The callback for when a PUBLISH message is received from the server.
# This should not be called.
def on_message(client, userdata, msg): 
    print(msg.topic + " " + str(msg.payload))

# function to initially make all lists size 10 contain 0's
def init_list():
    i = 0
    while i < 10: 
        ranger1_dist.append(0)
        ranger2_dist.append(0)
        ranger1_dist_avg.append(0)
        ranger2_dist_avg.append(0)
        i = i + 1

# function to decide which way you're moving
def decide():
    # ALL OF THIS IS FOR THE HTML REQUEST / SERVER
    # This header sets the HTTP request's mimetype to `application/json`. This
    # means the payload of the HTTP message will be formatted as a json ojbect
    hdr = {
        'Content-Type': 'application/json',
        'Authorization': None #not using HTTP secure
    }

    sum1 = 0
    sum2 = 0

    # sum up all the values in both distance arrays
    for i in range(9, 0, -1):
        sum1 = sum1 + ranger1_dist_avg[i] - ranger1_dist_avg[i-1]
        sum2 = sum2 + ranger2_dist_avg[i] - ranger2_dist_avg[i-1]

    # only print things out if someone is standing between the sensors 
    if(not(ranger1_dist[9] == 120 and ranger2_dist[9] == 120)):
        payload = { 'time': str(datetime.now()), 'event': "Pending"}

        # decide whether the data is clean enough to conclude movement / standing
        # another part to the threshold we added as a global variable at the top
        checkIfStatement = False

        # the case if the user is standing still
        # added case of +- threshold for both sums to account for noise
        if((sum1 < threshold and sum1 > -(threshold)) and (sum2 < threshold and sum2 > -(threshold))):
            checkIfStatement = True

            # the distance is split into thirds since it is 120cm
            # if the first sensor reads it greater than 80 then standing right
            if(ranger1_dist[9] > 80):
                print("Still - Right")
                payload = {
                    'time': str(datetime.now()),
                    'event': "Still - Right"
                }

            # if the first sensor reads it less than 40 then standing left
            elif (ranger1_dist[9] < 40):
                print("Still - Left")
                payload = {
                    'time': str(datetime.now()),
                    'event': "Still - Left"
                }

            # if the first sensor reads it between 40 and 80 then standing center
            else:
                print("Still - Middle") 
                payload = {
                    'time': str(datetime.now()),
                    'event': "Still - Middle"
                }

        # if the sum of the left sensor is increasing and the right sensor is decreasing
        elif(sum1 > threshold and sum2 < -(threshold)):
            checkIfStatement = True
            print("Moving Right")
            payload = {
                'time': str(datetime.now()),
                'event': "Moving Right"
            }

        # if the sum of the left sensor is decreasing and the right sensor is increasing
        elif(sum2 > threshold and sum1 < -(threshold)):
            checkIfStatement = True
            print("Moving Left")
            payload = {
                'time': str(datetime.now()),
                'event': "Moving Left"
            }

        # if the data was clean, then send to http server to display on port 0.0.0.0:5000/log
        if(checkIfStatement):
            response = requests.post("http://0.0.0.0:5000/post-event", headers = hdr, data = json.dumps(payload))

# main function 
if __name__ == '__main__':
    # Connect to broker and start loop    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_hostname, broker_port, 60)

    # initialize all lists (Function created by us )
    init_list()

    # start the sampling
    client.loop_start()

    # message for the user to initialize the sensors and average arrays with proper values
    # we wait for 5 seconds to make sure the average arrays and other data streams can work
    # out the noise to provide better data
    print("Initializing the sensors please wait...")

    #indices for the while loop
    i = 0   # used to count to 5 seconds to initialize system
    j = 0   # used to count to 2 seconds to call decide()

    while True:
        # count to 5 seconds
        if(i < 25):
            i = i + 1

        # at 5 seconds, let the user know that you can move in front of the sensors
        elif(i == 25):
            print("you may now move in front of the sensor")
            i = i +1

        # run the info from the sensor
        else:
            # print("ranger1: " + str(ranger1_dist[-1:]) + ", ranger2: " + 
            #     str(ranger2_dist[-1:])) 

            # after 2 seconds (10 iterations through the loop), 
            # call decide() to see what direction the user is moving
            if(j == 10):
                decide()
                j = 0       # set the counter back to 0

            # increment j counter
            j = j + 1
            
        # default sleep timer given to us
        time.sleep(0.2)