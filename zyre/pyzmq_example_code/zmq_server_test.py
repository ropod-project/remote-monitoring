#!/usr/bin/env python

import zmq
import sys
import time


port = "5556"
ip = "192.168.1.103"

context = zmq.Context()
print ("Server is up...")
socket = context.socket(zmq.REP)
socket.bind ("tcp://*:%s" % port)

# Create PULL Socket
# pullSocket = context.socket(zmq.PULL)
# pullSocket.bind("tcp://"+ ip + ":%s" % port)

while True:
    #  Testing with REQ/REP socket
    # message = socket.recv()
    message = socket.recv(0)
    print ("Received request: ", message)

    # we can break the loop as soon as we receive a message
    # if message:
    #     break

    # testing with pullSocket
    # try:
    #     print("Inside try - server")
    #     msg = pullSocket.recv(flags=zmq.NOBLOCK)
    #     print ("Received message from client: ", msg)
    # except zmq.Again as e:
    #     print ("Waiting for message from client")

    # testing with recv and send string
    # try:
    #     print ("Waiting for reply ...")
    #     # message = socket.recv_string(0)
    #     message = socket.recv_string(flags = zmq.NOBLOCK)
    #     print("Received message is: ", message)
    # except zmq.Again as e:
    #     print ("Waiting for message from client")

    time.sleep (1)  
    socket.send(("Answer from the test server %s" % port).encode('ascii'))