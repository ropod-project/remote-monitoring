#!/usr/bin/env python

import zmq
import sys
import time

port = "5670"
# if len(sys.argv) > 1:
#     port =  sys.argv[1]
#     int(port)

print ('pyzmq_version: ', zmq.pyzmq_version())

context = zmq.Context()
print ("Connecting to server...")

# creating a zmq client using zmq.REQ
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%s" % port)

# contin_loop = True

while True:
    print ("Sending request...")
    # socket.send(("Hello from the test client").encode('ascii'))
    socket.send(("GET_ROPOD_LIST").encode('ascii'))

    # Receiving message
    message = socket.recv()
    # message = socket.recv(flags = zmq.NOBLOCK)

    print ("Received reply [", message, "]")

    time.sleep(1)

print('Every thing went well.')