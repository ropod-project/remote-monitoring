from __future__ import print_function
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
        '''Returns a list of all known robot names.
        '''
        collection_name = Config.ROBOT_COLLECTION
        client = pm.MongoClient(port=self.db_port)
        db = client[self.db_name]
        collection = db[collection_name]
        docs = collection.find({})
        robots = [doc['name'] for doc in docs]
        return robots

    def get_robot_smart_wheel_count(self, robot_id):
        '''Returns the number of smart wheels of the given robot.

        Keyword arguments:
        robot_id -- ID of a robot

        '''
        collection_name = Config.ROBOT_COLLECTION
        client = pm.MongoClient(port=self.db_port)
        db = client[self.db_name]
        collection = db[collection_name]
        doc = collection.find_one({'name': robot_id})
        if doc:
            return doc['smart_wheel_count']
        print('{0} does not exist'.format(robot_id))
        return 0

    def get_experiments(self):
        '''Returns a list of dictionaries of the form
        {
            "id": experiment_id,
            "name": descriptive_experiment_name
        }
        '''
        collection_name = Config.EXPERIMENT_COLLECTION
        client = pm.MongoClient(port=self.db_port)
        db = client[self.db_name]
        collection = db[collection_name]
        docs = collection.find({})
        experiments = [{'id': doc['id'], 'name': doc['name']} for doc in docs]
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
