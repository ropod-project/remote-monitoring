'''
Zyre communication (receiver) in python using Pyre library

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

n = Pyre("receiver_node")
print('Join group [CHAT]')
n.join("CHAT")

print('node START')
n.start()

msg_data = {
  "header": {
    "type": "CMD",
    "version": "0.1.0",
    "metamodel": "ropod-msg-schema.json",
    "msg_id": "0d05d0bc-f1d2-4355-bd88-edf44e2475c8",
    "timestamp": "2017-11-11T11:11:00Z"
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
        "information": "MOBIDIK"
      }

msg_broadcast_name = str(n.name())
wsp_msg = 'whisper sample message'
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
                if item['command'] == "GOTO":
                    answers['information'] = item['location']
                elif item['command'] == "POSE":
                    answers['information'] = "0, 10, 20"
                elif item['command'] == "RESUME":
                    answers['information'] = "RESUME received"
                elif item['command'] == "STOP":
                    answers['information'] = "Robot stopped"
                
                answers['command'] = "ANSWER"
                msg_data['payload']['answerList'][0] = answers
                jmsg_data = json.dumps(msg_data).encode('utf-8')
                n.whisper(sender_uuid, jmsg_data)
                print("message sent")

print('Finished')
