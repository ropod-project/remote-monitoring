#!/usr/bin/env python

import zmq
import sys
import time

import json
# from decimal import Decimal
# from base64 import b64encode, b64decode
# from json import dumps, loads, JSONEncoder
# import pickle



port = "5670"
context = zmq.Context()
print ("Connecting to server...")

# creating a zmq client using zmq.REQ
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%s" % port)

# ---------------------------------------
# contin_loop = True
# while True:
#     print ("Sending request...")
#     # socket.send(("Hello from the test client").encode('ascii'))
#     socket.send(("GET_ROPOD_LIST").encode('ascii'))
#     # Receiving message
#     message = socket.recv()
#     # message = socket.recv(flags = zmq.NOBLOCK)
#     print ("Received reply [", message, "]")
#     time.sleep(1)
# ---------------------------------------

# Test for jsonify the message and other operations
print ("Sending request...")
socket.send(("GET_ROPOD_LIST").encode('ascii'))

# Receiving message
message = socket.recv()

print ("Received reply [", message, "]")
print("message type:",type(message))

jm = json.loads(message.decode('utf8'))
print("jm type:", type(jm))
print("jm[0]: ",jm[0])
print('\n')

# getting the keys for column names
jkeys = jm[0].keys()
print("jm[0].keys: ",jkeys)
print('\n')

# getting the values for showing the data and later plotting
jvals = list()
for item in jm:
    jvals.append(item.values())

print("jvals: ",jvals)
print("jvals.len: ",len(jvals))
for i in jvals:
    print(i)
# print("jval[:,1]: ",[row[0] for row in jvals])

print('\n')
print('\n')

print('Every thing went well.')