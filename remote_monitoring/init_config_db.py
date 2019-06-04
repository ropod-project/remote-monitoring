#!/usr/bin/env python
'''This module reads a yaml config file and inserts all the dictionaries in
collections dictionary into mongo db.
'''

from __future__ import print_function

import os
import glob
import yaml
from PIL import Image
import pymongo as pm

from remote_monitoring.common import Config

CONFIG_FILE = "config/init_config.yaml"

def init_collection(db_obj, config_collections, collection_name):
    """Initialise collection with all the documents in mongo db based on the config
    file.

    :collection_name: string
    :returns: None

    """
    print('Initialising "{0}" collection'.format(collection_name))
    collection = db_obj[collection_name]
    collection.insert_many(config_collections[collection_name])

def get_map_dict():
    code_dir = os.path.abspath(os.path.dirname(__file__))
    main_dir = os.path.dirname(code_dir)
    occ_grid_dir = os.path.join(main_dir, 'occupancy_grids')
    map_dir = os.path.join(code_dir, 'static/generated_maps')
    # make directory is it doesn't exist. If is exists then clean it
    if not os.path.isdir(map_dir):
        os.makedirs(map_dir)
    else:
        ls_output = os.listdir(map_dir)
        for text_file in ls_output:
            try:
                os.remove(os.path.join(map_dir, text_file))
            except Exception as e:
                print('Encountered following error while removing existing maps\n'+ str(e))

    current_dir = os.getcwd()
    os.chdir(occ_grid_dir)
    maps = glob.glob('**/map.yaml', recursive=True)
    print(len(maps))
    map_dict_list = []

    for map_file in maps:
        if 'brsu' in map_file and 'osm' in map_file:
            map_dict = {}
            map_dict['name'] = map_file.replace('/', '_').split('.')[0]
            info = {}
            with open(map_file, 'r') as yaml_file:
                info = yaml.safe_load(yaml_file)

            # convert pgm to png and save it in static folder
            image_file_path = os.path.join(os.path.dirname(os.path.abspath(map_file)), info['image'])
            map_dict['path'] = os.path.join(map_dir, map_dict['name']+'.png')
            image = Image.open(image_file_path)
            image.save(map_dict['path'])

            map_dict_list.append(map_dict)

    print(map_dict_list)
    os.chdir(current_dir)

def main():
    ''' Read a config file and insert all dict as collections in mongo db
    '''
    config = Config()
    client = pm.MongoClient(port=config.db_port)

    # clear the database if it already exists
    if config.db_name in client.list_database_names():
        client.drop_database(config.db_name)

    db_obj = client[config.db_name]

    with open(CONFIG_FILE, "r") as file_obj:
        data = yaml.safe_load(file_obj)

    config_collections = data['collections']

    init_collection(db_obj, config_collections, Config.ROBOT_COLLECTION)
    init_collection(db_obj, config_collections, Config.EXPERIMENT_COLLECTION)
    init_collection(db_obj, config_collections, Config.MAP_COLLECTION)
    init_collection(db_obj, config_collections, Config.QUERY_COLLECTION)
    get_map_dict()

if __name__ == "__main__":
    main()
