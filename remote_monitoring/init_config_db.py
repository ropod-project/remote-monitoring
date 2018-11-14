#!/usr/bin/env python
from __future__ import print_function
import pymongo as pm
from remote_monitoring.common import Config

robot_ids = ['ropod_001', 'ropod_002']
experiments = [{'id': 'linear_motion', 'name': 'Linear motion'},
               {'id': 'in_place_rotation', 'name': 'In-place rotation'},
               {'id': 'area_navigation', 'name': 'Area navigation'}]

config = Config()
client = pm.MongoClient(port=config.db_port)
db = client[config.db_name]

print('Initialising "{0}" collection'.format(Config.ROBOT_COLLECTION))
collection = db[Config.ROBOT_COLLECTION]
for robot_id in robot_ids:
    doc = dict()
    doc['name'] = robot_id
    collection.insert_one(doc)

print('Initialising "{0}" collection'.format(Config.EXPERIMENT_COLLECTION))
collection = db[Config.EXPERIMENT_COLLECTION]
for experiment in experiments:
    doc = experiment
    collection.insert_one(doc)
