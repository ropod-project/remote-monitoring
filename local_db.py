import pymongo as pm

from constants import VariableConstants
from db import DbConnection

class RopodAdminQueries(object):
    @staticmethod
    def get_all_ropods(db_connection):
        cursor = db_connection.collection.find()
        hospitals = list()
        ids = list()
        ip_addresses = list()
        for ropod in cursor:
            hospitals.append(ropod['hospital'])
            ids.append(ropod['id'])
            ip_addresses.append(ropod['ip_address'])
        return hospitals, ids, ip_addresses

    @staticmethod
    def get_hospital_names(db_connection):
        cursor = db_connection.collection.find().distinct('hospital')
        hospital_names = list()
        for hospital in cursor:
            hospital_names.append(hospital)
        return hospital_names

    @staticmethod
    def get_hospital_ropod_ids(db_connection, hospital_name):
        cursor = db_connection.collection.find({ 'hospital': hospital_name }, { 'id': 1 })
        ids = list()
        for row in cursor:
            ids.append(row['id'])
        return ids

    @staticmethod
    def get_black_box_ip(db_connection, hospital_name, ropod_id):
        doc = db_connection.collection.find_one({ 'hospital': hospital_name, 'id': ropod_id })
        ip_address = doc['ip_address']
        return ip_address

    @staticmethod
    def add_new_ropod(db_connection, hospital_name, ropod_id, ip_address):
        db_connection.collection.insert_one( {  'hospital': hospital_name, 'id': ropod_id, 'ip_address': ip_address } )

    @staticmethod
    def update_existing_ropod(db_connection, old_hospital_name, old_id, old_ip_address, new_hospital_name, new_id, new_ip_address):
        db_connection.collection.update_one( { 'hospital': old_hospital_name, 'id': old_id },
        { '$set': {  'hospital': new_hospital_name, 'id': new_id, 'ip_address': new_ip_address } } )

    @staticmethod
    def delete_ropod(db_connection, hospital_name, ropod_id, ip_address):
        db_connection.collection.delete_one( { 'hospital': hospital_name, 'id': ropod_id, 'ip_address': ip_address } )
