'''
Zyre communication (sender) in python using Pyre library.
This program will run on the server and asks robot to send 
information.
This program connects to a zyre group and when we decided 
it starts to get a serries of queries from another program 
that we choose.   

Author: Mohammadali Varfan
Contact information: varfanm@live.com
'''

import pyre
from pyre import Pyre

from pyre import zhelper
import zmq
import uuid
import logging
import sys
import json
import time


n = Pyre("sender_node")
n.join("ROPOD")
try:
	n.start()
except:
	print('cannot start node')
# print(n)

nodes_list = dict()

t = time.localtime()
current_time = str(t[0])+"-"+str(t[1])+"-"+str(t[2])+"T"+str(t[3])+":"+str(t[4])+":"+str(t[5])+"Z"

features_list = ['robotID', 'sensors', 'timestamp']
start_query_time = "2017-12-10 3:55:40"
end_query_time = "2017-12-10 11:25:40"


msg_data = {
  "header": {
    "type": "VARIABLE_QUERY",
    "version": "0.1.0",
    "metamodel": "ropod-msg-schema.json",
    "msg_id": "0d05d0bc-f1d2-4355-bd88-edf44e2475c8",
    "timestamp": current_time
  },
  "payload": {
    "metamodel": "ropod-demo-cmd-schema.json",
    "commandList":[
      { 
        "command": "GETQUERY",
        "features": features_list,
        "start_time": start_query_time,	
        "end_time": end_query_time
      }
     ]
  }
}

queries = [
      { 
        "command": "SENDINFO",
        "features": features_list
      }]

msg_name_request = "NameRequest"
dest_name = "receiver_node"
get_info = True
get_queries = True
send_next_query = False
k = 0
q = 0

print('press enter to start the program')
k = input()

# send an order to all nodes(shout) to send their names
try:
	n.shout("ROPOD", msg_name_request.encode('utf-8'))
except:
	print('cannot send message')

while get_queries:
	rec_msg = n.recv()
	msg_type = rec_msg[0].decode('utf-8')

	# get all the nodes in the group
	sender_uuid = uuid.UUID(bytes=rec_msg[1])
	sender_name = rec_msg[2].decode('utf-8')
	nodes_list[sender_name] = sender_uuid

	data = rec_msg[-1]
	data = data.decode('utf-8')
	if str(msg_type) == 'SHOUT' or str(msg_type) == 'WHISPER':
		try:
			jdata = json.loads(data)
			if jdata['payload']['answerList'][0]['command'] == "ANSWER":
				# send_next_query = True
				print('received answer:')
				print(jdata['payload']['answerList'])
				received_answer = jdata['payload']['answerList']
		except Exception as e:
			# print('Exception: ', e)
			pass

	if send_next_query:
		msg_data['payload']['commandList'][0] = {"command": "GETQUERY",
		"features": features_list,
		"start_time": start_query_time,
		"end_time": end_query_time
		}
		jmsg_data = json.dumps(msg_data).encode('utf-8')
		dest_uuid = nodes_list[dest_name]
		n.whisper(dest_uuid, jmsg_data)
		send_next_query = False

	if get_info:
		msg_data['payload']['commandList'][0] = {"command": "SENDINFO"}
		jmsg_data = json.dumps(msg_data).encode('utf-8')
		dest_uuid = nodes_list[dest_name]
		n.whisper(dest_uuid, jmsg_data)
		send_next_query = True
		get_info = False

n.stop()
print('Program Finished')