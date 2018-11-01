import pymongo as pm
from flask_socketio import SocketIO

socketio = SocketIO()

class Config(object):
    ROBOT_COLLECTION = 'robots'
    EXPERIMENT_COLLECTION = 'experiments'

    def __init__(self):
        self.db_name = 'remote_monitoring_config'
        self.db_port = 27017

    def get_robots(self):
        collection_name = Config.ROBOT_COLLECTION
        client = pm.MongoClient(port=self.db_port)
        db = client[self.db_name]
        collection = db[collection_name]
        docs = collection.find({})
        robots = list()
        for doc in docs:
            robots.append(doc['name'])
        return robots

    def get_experiments(self):
        collection_name = Config.EXPERIMENT_COLLECTION
        client = pm.MongoClient(port=self.db_port)
        db = client[self.db_name]
        collection = db[collection_name]
        docs = collection.find({})
        experiments = list()
        for doc in docs:
            experiment = dict()
            experiment['id'] = doc['id']
            experiment['name'] = doc['name']
            experiments.append(experiment)
        return experiments

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
