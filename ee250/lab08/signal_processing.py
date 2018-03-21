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

    for i in range(9, 0, -1):
        sum1 = sum1 + ranger1_dist_avg[i] - ranger1_dist_avg[i-1]
        sum2 = sum2 + ranger2_dist_avg[i] - ranger2_dist_avg[i-1]

    if(sum1 < 10 and sum1 > -10 and sum2 < 10 and sum2 > -10):
        print("Standing still")
        if (ranger1_dist_avg[9] > ranger2_dist_avg[9]):
            print("Still right")
        elif (ranger2_dist_avg[9] > ranger1_dist_avg[9]):
            print("Still left")
        else:
            print("Still center") 
    elif(sum1 > 10 and sum2 < -10):
        print("moving right")
    elif(sum2 > 10 and sum1 < -10):
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

    # message for the user 
    print("Please wait 5 seconds for system to initialize...")

    #indices for the while loop
    i = 0
    j = 0

    while True:
        """ You have two lists, ranger1_dist and ranger2_dist, which hold a window
        of the past MAX_LIST_LENGTH samples published by ultrasonic ranger 1
        and 2, respectively. The signals are published roughly at intervals of
        200ms, or 5 samples/second (5 Hz). The values published are the 
        distances in centimeters to the closest object. Expect values between 
        0 and 512. However, these rangers do not detect people well beyond 
        ~125cm. """

        if(i < 25):
            i = i + 1

        elif(i == 25):
            print("you may now move in front of the sensor")
            i = i +1

        else:
            # print("ranger1: " + str(ranger1_dist[-1:]) + ", ranger2: " + 
            #     str(ranger2_dist[-1:])) 

            # print("ranger1 average: " + str(ranger1_dist_avg[-1:]) + ", ranger2 average: " + 
            #     str(ranger2_dist_avg[-1:]))
            if(j == 10):
                decide()
                j = 0

            j = j + 1
            
        
        time.sleep(0.2)
