'''
Zyre communication (receiver) in python using Pyre library.
This program will be run on the robot.

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
from pymongo import MongoClient


col_name = 'database'
con = MongoClient()
db = con.col_name


# establishing and joining a zyre group
n = Pyre("receiver_node")
n.join("CHAT")
n.start()

# print(n.name(), n.uuid())

t = time.localtime()
current_time = str(t[0])+"-"+str(t[1])+"-"+str(t[2])+"T"+str(t[3])+":"+str(t[4])+":"+str(t[5]+"Z")

msg_data = {
  "header": {
    "type": "CMD",
    "version": "0.1.0",
    "metamodel": "ropod-msg-schema.json",
    "msg_id": "0d05d0bc-f1d2-4355-bd88-edf44e2475c8",
    "timestamp": current_time
  },
  "payload": {
    "metamodel": "ropod-demo-cmd-schema.json",
    "answerList":[
      { 
        "command": "GOTO",
        "location": "START"
      }
     ]
  }
}

answers ={ 
        "command": "ANSWER",
        "information": ""
      }

msg_broadcast_name = str(n.name())
while True:
    have_command = False
    rec_msg = n.recv()
    msg_type = rec_msg[0].decode('utf-8')
    sender_uuid = uuid.UUID(bytes=rec_msg[1])
    sender_name = rec_msg[2].decode('utf-8')

    data = rec_msg[-1]
    data = data.decode('utf-8')
    if str(data) == 'NameRequest':
        n.shout("CHAT", msg_broadcast_name.encode('utf-8'))

    if str(msg_type) == 'SHOUT' or str(msg_type) == 'WHISPER':
        try:
            jdata = json.loads(data)
            have_command = True
        except Exception as e:
            print('Exception: ', e)

        if have_command:
            for item in jdata['payload']['commandList']:
                if item['command'] == "ASKINFORMATION":
                    features_list = item['features']
                    features = []
                    for f in features_list:
                        features.append({f:1})
                    start_query_time = item['start_time']
                    end_query_time = item['end_time']

                    # get query
                    query_result = db.col_name.find({'timestamp': {$gte: start_query_time, $lt: end_query_time}},
                                                    {$or : features})
                    # create the response
                    answers['information'] = query_result              
                    answers['command'] = "ANSWER"
                    msg_data['payload']['answerList'][0] = answers

                    # sending the response
                    jmsg_data = json.dumps(msg_data).encode('utf-8')
                    n.whisper(sender_uuid, jmsg_data)
                    break
                    # print("message sent")

print('Finished')


# "commandList":[
#       { 
#         "command": "ASKINFORMATION",
#         "features": features_list
#         "start_time": start_query_time
#         "end_time": end_query_time
#       }
#      ]