import zmq

zmq_context = zmq.Context()
port = "5670"

msg_data = {
    "header":
    {
        "type": "VARIABLE_QUERY",
        "version": "0.1.0",
        "metamodel": "ropod-msg-schema.json",
        "msg_id": "0d05d0bc-f1d2-4355-bd88-edf44e2475c8",
        "timestamp": ""
    },
    "payload":
    {
        "metamodel": "ropod-demo-cmd-schema.json",
        "commandList":
        [
            {
                "features": [],
                "start_time": "",
                "end_time": ""
            }
        ]
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
