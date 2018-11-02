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

robot_status_msg = {
    "header":
    {
        "type": "HEALTH-STATUS",
        "version": "0.1.0",
        "metamodel": "ropod-msg-schema.json",
        "msgId": None,
        "timestamp": None
    },
    "payload":
    {
        "metamodel": "ropod-component-monitor-schema.json",
        "robotId": None,
        "monitors": None
    }
}
