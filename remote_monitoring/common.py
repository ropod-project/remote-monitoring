import zmq
from flask_socketio import SocketIO

socketio = SocketIO()

from pymongo import MongoClient
client = MongoClient()

zmq_context = zmq.Context()
port = "5670"

msg_data = {
    "header":
    {
        "type": "",
        "version": "0.1.0",
        "metamodel": "ropod-msg-schema.json",
        "timestamp": ""
    },
    "payload":
    {
        "metamodel": "ropod-demo-cmd-schema.json",
        "senderId": ""
    }
}

ropod_status_msg = {
    "header":
    {
        "type": "STATUS",
        "version": "0.1.0",
        "metamodel": "ropod-msg-schema.json",
        "msg_id": "0d05d0bc-f1d2-4355-bd88-edf44e2475c8",
        "timestamp": ""
    },
    "payload":
    {
        "metamodel": "ropod-status-schema.json",
        "status":
        {
            "hardware_devices":
            {
                "battery": 56.4,
                "motors_on": True,
                "wheel1": True,
                "wheel2": True,
                "wheel3": True,
                "wheel4": False,
                "wifi": 89
            },
            "sensors":
            {
                "joypad": False,
                "laser_front": True,
                "laser_back": True
            },
            "software":
            {
                "ros_master": True,
                "ros_nodes":
                {
                    "node_1": False,
                    "node_n": True
                },
                "localised": True,
                "laser_map_matching": 66.5
            }
        }
    }
}

def communicate_zmq(data):
    socket = zmq_context.socket(zmq.REQ)
    socket.connect("tcp://localhost:%s" % port)
    socket.send(data.encode('ascii'))
    reply = socket.recv()
    return reply

def get_deployed_ropods():
    cursor = client.deployed_ropods.ropods.find()
    ropods = []
    for r in cursor:
        ropods.append(r['ropod_name'])
    return ropods

def get_deployed_black_boxes():
    cursor = client.deployed_ropods.black_boxes.find()
    black_boxes = []
    for b in cursor:
        black_boxes.append(b)
    return black_boxes

