import pymongo as pm

from constants import VariableConstants
from db import DbConnection

class RopodAdminQueries(object):
    @staticmethod
    def get_hospital_names(db_connection):
        cursor = db_connection.collection.find().distinct('hospital')
        hospital_names = list()
        for hospital in cursor:
            hospital_names.append(hospital)
        return hospital_names

    @staticmethod
    def get_hospital_black_box_ips(db_connection, hospital_name):
        cursor = db_connection.collection.find({ 'hospital': hospital_name }, { 'ip_address': 1 })
        ips = list()
        for row in cursor:
            ips.append(row['ip_address'])
        return ips

    @staticmethod
    def add_new_ropod(db_connection, hospital_name, ip_address):
        db_connection.collection.insert_one( {  'hospital': hospital_name, 'ip_address': ip_address } )
