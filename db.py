import pymongo as pm

from constants import VariableConstants

class DbConnection(object):
    def __init__(self, host_address, database_name, collection_name):
        self.client = pm.MongoClient(host_address)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

class DbQueries(object):
    @staticmethod
    def get_data(db_connection, key, start_timestamp, end_timestamp):
        data = list()
        data_labels = list()
        cursor = None
        if key == VariableConstants.POSE:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "pos_x" : "$pos_x",
                                    "pos_y" : "$pos_y",
                                    "pos_t" : "$pos_t"
                                    }
                        }])
            for r in cursor:
                data.append([ r['pos_x'], r['pos_y'], r['pos_t'] ])
            data_labels = ['x', 'y', 'theta']
        elif key == VariableConstants.BATTERY_STATUS:
            cursor = list()
        elif key == VariableConstants.EXTERNAL_SOURCE_STATUS:
            cursor = list()
        elif key == VariableConstants.WHEEL_FAULT_STATUS:
            cursor = list()
        elif key == VariableConstants.WHEEL_CURRENTS:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "cur_j1" : "$cur_j1",
                                    "cur_j2" : "$cur_j2",
                                    "cur_j3" : "$cur_j3",
                                    "cur_j4" : "$cur_j4"
                                    }
                        }])
            for r in cursor:
                data.append([ r['cur_j1'], r['cur_j2'], r['cur_j3'], r['cur_j4'] ])
            data_labels = ['Joint 1', 'Joint 2', 'Joint 3', 'Joint 4']
        elif key == VariableConstants.WHEEL_ANGLES:
            cursor = list()
        elif key == VariableConstants.WHEEL_VELOCITIES:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "vel_j1" : "$vel_j1",
                                    "vel_j2" : "$vel_j2",
                                    "vel_j3" : "$vel_j3",
                                    "vel_j4" : "$vel_j4"
                                    }
                        }])
            for r in cursor:
                data.append([ r['vel_j1'], r['vel_j2'], r['vel_j3'], r['vel_j4'] ])
            data_labels = ['Joint 1', 'Joint 2', 'Joint 3', 'Joint 4']
        elif key == VariableConstants.WHEEL_TORQUES:
            cursor = list()
        elif key == VariableConstants.EXPECTED_WHEEL_VELOCITIES:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "evel_j1" : "$evel_j1",
                                    "evel_j2" : "$evel_j2",
                                    "evel_j3" : "$evel_j3",
                                    "evel_j4" : "$evel_j4"
                                    }
                        }])
            for r in cursor:
                data.append([ r['evel_j1'], r['evel_j2'], r['evel_j3'], r['evel_j4'] ])
            data_labels = ['Joint 1', 'Joint 2', 'Joint 3', 'Joint 4']
        elif key == VariableConstants.ROBOT_VELOCITY:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "lvel" : "$lvel",
                                    "tvel" : "$tvel",
                                    "avel" : "$avel"
                                    }
                        }])
            for r in cursor:
                data.append([ r['lvel'], r['tvel'], r['avel'] ])
            data_labels = ['longitudinal', 'transversal', 'angular']
        elif key == VariableConstants.ROBOT_VELOCITY_CMD:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "lvel_cmd" : "$lvel_cmd",
                                    "tvel_cmd" : "$tvel_cmd",
                                    "avel_cmd" : "$avel_cmd"
                                    }
                        }])
            for r in cursor:
                data.append([ r['lvel_cmd'], r['tvel_cmd'], r['avel_cmd'] ])
            data_labels = ['longitudinal', 'transversal', 'angular']

        return data, data_labels
