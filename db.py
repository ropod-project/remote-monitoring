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
                                    "pose_t" : "$pose_t"
                                    }
                        }])
            position_x = list()
            position_y = list()
            orientation = list()
            for r in cursor:
                position_x.append([ r['timestamp'], r['pos_x'] ])
                position_y.append([ r['timestamp'], r['pos_y'] ])
                orientation.append([ r['timestamp'], r['pose_t'] ])
            data.append(position_x)
            data.append(position_y)
            data.append(orientation)
            data_labels = ['x', 'y', 'theta']
        elif key == VariableConstants.BATTERY_STATUS:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "battery_status" : "$battery_status"
                                    }
                        }])
            status = list()
            for r in cursor:
                status.append([ r['timestamp'], r['battery_status'] ])
            data.append(status)
            data_labels = ['Battery status']
        elif key == VariableConstants.EXTERNAL_SOURCE_STATUS:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "ext_source_status" : "$ext_source_status"
                                    }
                        }])
            status = list()
            for r in cursor:
                status.append([ r['timestamp'], r['ext_source_status'] ])
            data.append(status)
            data_labels = ['External source status']
        elif key == VariableConstants.WHEEL_FAULT_STATUS:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "fault_status_j1" : "$fault_status_j1",
                                    "fault_status_j2" : "$fault_status_j2",
                                    "fault_status_j3" : "$fault_status_j3",
                                    "fault_status_j4" : "$fault_status_j4"
                                    }
                        }])
            data_j1 = list()
            data_j2 = list()
            data_j3 = list()
            data_j4 = list()
            for r in cursor:
                data_j1.append([ r['timestamp'], r['fault_status_j1'] ])
                data_j2.append([ r['timestamp'], r['fault_status_j2'] ])
                data_j3.append([ r['timestamp'], r['fault_status_j3'] ])
                data_j4.append([ r['timestamp'], r['fault_status_j4'] ])
            data.append(data_j1)
            data.append(data_j2)
            data.append(data_j3)
            data.append(data_j4)
            data_labels = ['Joint 1', 'Joint 2', 'Joint 3', 'Joint 4']
        elif key == VariableConstants.WHEEL_CURRENTS:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "current_j1" : "$current_j1",
                                    "current_j2" : "$current_j2",
                                    "current_j3" : "$current_j3",
                                    "current_j4" : "$current_j4"
                                    }
                        }])
            data_j1 = list()
            data_j2 = list()
            data_j3 = list()
            data_j4 = list()
            for r in cursor:
                data_j1.append([ r['timestamp'], r['current_j1'] ])
                data_j2.append([ r['timestamp'], r['current_j2'] ])
                data_j3.append([ r['timestamp'], r['current_j3'] ])
                data_j4.append([ r['timestamp'], r['current_j4'] ])
            data.append(data_j1)
            data.append(data_j2)
            data.append(data_j3)
            data.append(data_j4)
            data_labels = ['Joint 1', 'Joint 2', 'Joint 3', 'Joint 4']
        elif key == VariableConstants.WHEEL_ANGLES:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "angle_j1" : "$angle_j1",
                                    "angle_j2" : "$angle_j2",
                                    "angle_j3" : "$angle_j3",
                                    "angle_j4" : "$angle_j4"
                                    }
                        }])
            data_j1 = list()
            data_j2 = list()
            data_j3 = list()
            data_j4 = list()
            for r in cursor:
                data_j1.append([ r['timestamp'], r['angle_j1'] ])
                data_j2.append([ r['timestamp'], r['angle_j2'] ])
                data_j3.append([ r['timestamp'], r['angle_j3'] ])
                data_j4.append([ r['timestamp'], r['angle_j4'] ])
            data.append(data_j1)
            data.append(data_j2)
            data.append(data_j3)
            data.append(data_j4)
            data_labels = ['Joint 1', 'Joint 2', 'Joint 3', 'Joint 4']
        elif key == VariableConstants.WHEEL_VELOCITIES:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "velocity_j1" : "$velocity_j1",
                                    "velocity_j2" : "$velocity_j2",
                                    "velocity_j3" : "$velocity_j3",
                                    "velocity_j4" : "$velocity_j4"
                                    }
                        }])
            data_j1 = list()
            data_j2 = list()
            data_j3 = list()
            data_j4 = list()
            for r in cursor:
                data_j1.append([ r['timestamp'], r['velocity_j1'] ])
                data_j2.append([ r['timestamp'], r['velocity_j2'] ])
                data_j3.append([ r['timestamp'], r['velocity_j3'] ])
                data_j4.append([ r['timestamp'], r['velocity_j4'] ])
            data.append(data_j1)
            data.append(data_j2)
            data.append(data_j3)
            data.append(data_j4)
            data_labels = ['Joint 1', 'Joint 2', 'Joint 3', 'Joint 4']
        elif key == VariableConstants.WHEEL_TORQUES:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "torque_j1" : "$torque_j1",
                                    "torque_j2" : "$torque_j2",
                                    "torque_j3" : "$torque_j3",
                                    "torque_j4" : "$torque_j4"
                                    }
                        }])
            data_j1 = list()
            data_j2 = list()
            data_j3 = list()
            data_j4 = list()
            for r in cursor:
                data_j1.append([ r['timestamp'], r['torque_j1'] ])
                data_j2.append([ r['timestamp'], r['torque_j2'] ])
                data_j3.append([ r['timestamp'], r['torque_j3'] ])
                data_j4.append([ r['timestamp'], r['torque_j4'] ])
            data.append(data_j1)
            data.append(data_j2)
            data.append(data_j3)
            data.append(data_j4)
            data_labels = ['Joint 1', 'Joint 2', 'Joint 3', 'Joint 4']
        elif key == VariableConstants.EXPECTED_WHEEL_VELOCITIES:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "exp_velocity_j1" : "$exp_velocity_j1",
                                    "exp_velocity_j2" : "$exp_velocity_j2",
                                    "exp_velocity_j3" : "$exp_velocity_j3",
                                    "exp_velocity_j4" : "$exp_velocity_j4"
                                    }
                        }])
            data_j1 = list()
            data_j2 = list()
            data_j3 = list()
            data_j4 = list()
            for r in cursor:
                data_j1.append([ r['timestamp'], r['exp_velocity_j1'] ])
                data_j2.append([ r['timestamp'], r['exp_velocity_j2'] ])
                data_j3.append([ r['timestamp'], r['exp_velocity_j3'] ])
                data_j4.append([ r['timestamp'], r['exp_velocity_j4'] ])
            data.append(data_j1)
            data.append(data_j2)
            data.append(data_j3)
            data.append(data_j4)
            data_labels = ['Joint 1', 'Joint 2', 'Joint 3', 'Joint 4']
        elif key == VariableConstants.ROBOT_VELOCITY:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "longitudinal_velocity" : "$longitudinal_velocity",
                                    "transversal_velocity" : "$transversal_velocity",
                                    "angular_velocity" : "$angular_velocity"
                                    }
                        }])
            longitudinal_velocity = list()
            transversal_velocity = list()
            angular_velocity = list()
            for r in cursor:
                longitudinal_velocity.append([ r['timestamp'], r['longitudinal_velocity'] ])
                transversal_velocity.append([ r['timestamp'], r['transversal_velocity'] ])
                angular_velocity.append([ r['timestamp'], r['angular_velocity'] ])
            data.append(longitudinal_velocity)
            data.append(transversal_velocity)
            data.append(angular_velocity)
            data_labels = ['Longitudinal', 'Transversal', 'Angular']
        elif key == VariableConstants.ROBOT_VELOCITY_CMD:
            cursor = db_connection.collection.aggregate([
                        { "$match": {
                                    "timestamp" : {"$gt": start_timestamp},
                                    "timestamp" : {"$lt": end_timestamp} }
                        },
                        { "$project": {
                                    "timestamp" : 1,
                                    "longitudinal_velocity_cmd" : "$longitudinal_velocity_cmd",
                                    "transversal_velocity_cmd" : "$transversal_velocity_cmd",
                                    "angular_velocity_cmd" : "$angular_velocity_cmd"
                                    }
                        }])
            longitudinal_velocity = list()
            transversal_velocity = list()
            angular_velocity = list()
            for r in cursor:
                longitudinal_velocity.append([ r['timestamp'], r['longitudinal_velocity_cmd'] ])
                transversal_velocity.append([ r['timestamp'], r['transversal_velocity_cmd'] ])
                angular_velocity.append([ r['timestamp'], r['angular_velocity_cmd'] ])
            data.append(longitudinal_velocity)
            data.append(transversal_velocity)
            data.append(angular_velocity)
            data_labels = ['Longitudinal', 'Transversal', 'Angular']

        return data, data_labels
