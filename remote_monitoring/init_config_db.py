#!/usr/bin/env python
from __future__ import print_function
import pymongo as pm
from remote_monitoring.common import Config

robot_ids = ['ropod_001', 'ropod_002', 'ropod_003']
smart_wheel_counts = {'ropod_001': 4, 'ropod_002': 4, 'ropod_003': 4}
experiments = [{'id': 'linear_motion', 'name': 'Linear motion'},
               {'id': 'in_place_rotation', 'name': 'In-place rotation'},
               {'id': 'area_navigation', 'name': 'Area navigation'},
               {'id': 'path_planner_area_navigation', 'name': 'Area navigation using Path planner'},
               {'id': 'elevator_entering', 'name': 'Elevator entering'},
               {'id': 'dock', 'name': 'Docking'},
               {'id': 'undock', 'name': 'Undocking'},
               {'id': 'nav_dock_undock', 'name': 'Navigation, docking, and undocking'},
               {'id': 'dock_and_enter_elevator', 'name': 'Docking and elevator entering'}]
               
queries = [ {'id': 'get_all_ongoing_tasks', 'name': 'All ongoing tasks'},
            {'id': 'get_all_scheduled_tasks', 'name': 'All scheduled tasks'},
            {'id': 'get_robots_assigned_to_task', 'name': 'Robots assigned to task'},
            {'id': 'get_tasks_assigned_to_robot', 'name': 'Tasks assigned to robot'}]
            
maps = [{'name': 'amk-basement', 'path': '/static/maps/amk/basement.png',
         'display_scale': 0.15, 'width': 3942, 'height': 8659,
         'xrange': [-1250, 2500], 'yrange': [-7500, 2700],
         'origin_x': -1250, 'origin_y': 1250, 'resolution': 0.02},
        {'name': 'brsu-c-floor0', 'path': '/static/maps/brsu/c-floor0.png',
         'display_scale': 0.15, 'width': 4598, 'height': 4228,
         'xrange': [-1200, 3500], 'yrange': [-200, 4000],
         'origin_x': -1250, 'origin_y': 4000, 'resolution': 0.02}]

config = Config()
client = pm.MongoClient(port=config.db_port)
# clear the database if it already exists
if config.db_name in client.list_database_names():
    client.drop_database(config.db_name)
db = client[config.db_name]

print('Initialising "{0}" collection'.format(Config.ROBOT_COLLECTION))
collection = db[Config.ROBOT_COLLECTION]
for robot_id in robot_ids:
    doc = dict()
    doc['name'] = robot_id
    doc['smart_wheel_count'] = smart_wheel_counts[robot_id]
    collection.insert_one(doc)

print('Initialising "{0}" collection'.format(Config.EXPERIMENT_COLLECTION))
collection = db[Config.EXPERIMENT_COLLECTION]
for experiment in experiments:
    doc = experiment
    collection.insert_one(doc)

print('Initialising "{0}" collection'.format(Config.MAP_COLLECTION))
collection = db[Config.MAP_COLLECTION]
for m in maps:
    doc = m
    collection.insert_one(doc)
collection.insert_one({'current_map':'brsu-c-floor0'})

print('Initialising "{0}" collection'.format(Config.QUERY_COLLECTION))
collection = db[Config.QUERY_COLLECTION]
for query in queries :
    collection.insert_one(query)
