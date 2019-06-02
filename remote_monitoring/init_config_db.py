#!/usr/bin/env python
'''This module reads a yaml config file and inserts all the dictionaries in
collections dictionary into mongo db.
'''

from __future__ import print_function

import yaml
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

if __name__ == "__main__":
    main()
