#!/usr/bin/env python

import zmq
import sys
import time


port = "5556"
ip = "192.168.1.103"

context = zmq.Context()
print ("Connecting to server...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:%s" % port)

# Create PULL Socket
# pullSocket = context.socket(zmq.PULL)
# pullSocket.connect("tcp://*:%s" % port)

# using a poller
# poller = zmq.Poller()
# poller.register(socket)

# poller2 = zmq.Poller()
# poller2.register(socket2)

while True:
    print ("Sending request...")
    socket.send(("Hello from the test client").encode('ascii'))

    # Receiving message
    message = socket.recv()
    # message = socket.recv(flags = zmq.NOBLOCK)

    print ("Received reply [", message, "]")

    # testing with pullSocket
    # try:
    #     msg = pullSocket.recv(flags=zmq.NOBLOCK)
    #     print ("Received reply: ", msg)
    # except zmq.Again as e:
    #     print ("Waiting for message from server")

    # testing with recv and send string
    # print ("Sending message ...")
    # socket.send_string("Hello from the test client")
    # print("message sent")

    # try:
    #     print ("Waiting for reply ...")
    #     # message = socket.recv_string(0)
    #     message = socket.recv_string(flags = zmq.NOBLOCK)
    #     print("Received message is: ", message)
    # except zmq.Again as e:
    #     print ("Waiting for message from server")

    # testing with poller
    # events = dict(poller.poll(0))
    # events = dict(poller.poll(zmq.NOBLOCK))
    # events = dict(poller2.poll(0))
    # print('events: ', events)
    # if socket2 in events:
    #     print('received a message')
    #     msg = socket2.recv()
    #     print("received %r" % msg)
    #     if msg == 'quit':
    #         break
    # else:
    #     # no message to recv, do other things
    #     print('no message to recv, do other things')
    #     time.sleep(1)

    time.sleep (1)