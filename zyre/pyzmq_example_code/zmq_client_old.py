# pzymq tutorial:
# https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/client_server.html

#!/usr/bin/env python

import zmq
import sys
import time

port = "5670"
ip = "127.0.0.1"
# if len(sys.argv) > 1:
#     port =  sys.argv[1]
#     int(port)

print ('pyzmq_version: ', zmq.pyzmq_version())

context = zmq.Context()
rec_context = zmq.Context()
print ("Connecting to server...")

# creating a zmq client using zmq.REQ
socket = context.socket(zmq.XREQ)
socket.connect ("tcp://"+ ip + ":%s" % port)

socket2 = context.socket(zmq.XREQ)
socket2.connect ("tcp://"+ ip + ":%s" % port)

rec_socket = rec_context.socket(zmq.SUB)
rec_socket.connect ("tcp://"+ ip + ":%s" % port)
rec_socket.setsockopt_string(zmq.SUBSCRIBE, '')

print ("Sending request...")
socket.send(("GET_ROPOD_LIST").encode('ascii'))
print('message sent.')

contin_loop = True
i = 0


# using a poller
poller = zmq.Poller()
poller.register(socket)

poller2 = zmq.Poller()
poller2.register(socket2)

while contin_loop:
    # print ("Sending request...")
    # socket.send(("GET_ROPOD_LIST").encode('ascii'))
    # print('message sent.')

    # get the reply
    # message = socket.recv()
    # print ("Received reply [", message, "]")
    
    # print('waiting for message')
    # message = rec_socket.recv()
    # try:
    #     print('waiting for message')
    #     # message = rec_socket.recv(zmq.NOBLOCK)
    #     # message = socket.recv(zmq.NOBLOCK)
    #     # message = socket.recv(0)
    #     # message = socket2.recv(flags = 0)
    #     # message = socket.recv_string(0)
    #     print ("Received reply [", message, "]")
    #     if message:
    #         contin_loop = False
    # except zmq.Again:
        # print('Faced error: ')

    # try:
    #     msg = socket.recv(zmq.NOBLOCK) # note NOBLOCK here
    # except zmq.Again:
    #     # no message to recv, do other things
    #     time.sleep(1)
    # else:
    #     print("received %r" % msg)
    #     if msg == 'quit':
    #         break

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
        # no message to recv, do other things
        # print('no message to recv, do other things')
        # time.sleep(1)


print("after recv")

