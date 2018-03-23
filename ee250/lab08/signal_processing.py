import paho.mqtt.client as mqtt
import time

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

def ranger1_callback(client, userdata, msg):
    global ranger1_dist
    if(int(msg.payload) > 120):
        msg.payload = "120"

    ranger1_dist.append(int(msg.payload))
    #truncate list to only have the last MAX_LIST_LENGTH values
    ranger1_dist = ranger1_dist[-MAX_LIST_LENGTH:]

    # calculate the average and append to the average list
    rng1 = 0
    for i in range(0, 10):
        rng1 = rng1 + ranger1_dist[i]

    rng1 = rng1 / 10

    ranger1_dist_avg.append(rng1)

    del ranger1_dist_avg[0]


def ranger2_callback(client, userdata, msg):
    global ranger2_dist
    if(int(msg.payload) > 120):
        msg.payload = "120"

    ranger2_dist.append(int(msg.payload))
    #truncate list to only have the last MAX_LIST_LENGTH values
    ranger2_dist = ranger2_dist[-MAX_LIST_LENGTH:]

    # calculate the average and append to the average list 
    rng2 = 0
    for i in range(0, 10):
        rng2 = rng2 + ranger2_dist[i]

    rng2 = rng2 / 10

    ranger2_dist_avg.append(rng2)

    del ranger2_dist_avg[0]

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

# function to initially make all lists contain 0's
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
    sum1 = 0
    sum2 = 0

    # sum up all the values in both distance arrays
    for i in range(9, 0, -1):
        sum1 = sum1 + ranger1_dist_avg[i] - ranger1_dist_avg[i-1]
        sum2 = sum2 + ranger2_dist_avg[i] - ranger2_dist_avg[i-1]

    # only print things out if someone is standing between the sensors 
    if(not(ranger1_dist[9] == 120 and ranger2_dist[9] == 120)):
        # the case if the user is standing still
        # added case of +- 10 for both sums to account for noise
        if((sum1 < threshold and sum1 > -(threshold)) and (sum2 < threshold and sum2 > -(threshold))):
            print("Standing still")

            # the distance is split into thirds since it is 120cm
            # if the first sensor reads it less than 40 then standing left
            # if the first sensor reads it between 40 and 80 then standing center
            # if the first sensor reads it greater than 80 then standing right
            if (ranger1_dist[9] > 80):
                print("Still right")
            elif (ranger1_dist[9] < 40):
                print("Still left")
            else:
                print("Still center") 

        # if the sum of the left sensor is increasing and the right sensor is decreasing
        elif(sum1 > threshold and sum2 < -(threshold)):
            print("moving right")

        # if the sum of the left sensor is decreasing and the right sensor is increasing
        elif(sum2 > threshold and sum1 < -(threshold)):
            print("moving left")

# main function 
if __name__ == '__main__':
    # Connect to broker and start loop    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_hostname, broker_port, 60)

    # initialize all lists
    init_list()

    # start the sampling
    client.loop_start()

    # message for the user to initialize the sensors and average arrays with proper values
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

            # after 2 seconds, call decide() to see what direction the user is moving
            if(j == 10):
                decide()    # call decide() to print direction or standing still
                j = 0       # set the counter back to 0

            # increment j counter
            j = j + 1
            
        
        # default sleep timer given to us
        time.sleep(0.2)
