import zmq
from flask_socketio import SocketIO

socketio = SocketIO()

import pymongo as pm

class Config(object):
    def __init__(self):
        self.db_name = 'remote_monitoring_config'

    def get_robots(self):
        collection_name = 'robots'
        client = pm.MongoClient()
        db = client[self.db_name]
        collection = db[collection_name]
        docs = collection.find({})
        robots = list()
        for doc in docs:
            robots.append(doc['name'])
        return robots

zmq_context = zmq.Context()
zmq_port = "5670"

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
    socket.connect("tcp://localhost:%s" % zmq_port)
    socket.send(data.encode('ascii'))
    reply = socket.recv()
    return reply
