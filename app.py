#!/usr/bin/env python

from flask import Flask, jsonify, render_template, request, redirect, url_for
from datetime import datetime

from constants import LocalDbConstants, DbConstants, VariableConstants
from db import DbConnection, DbQueries
from local_db import RopodAdminQueries

app = Flask(__name__)
local_db_connection = DbConnection('127.0.0.1', LocalDbConstants.DATABASE, LocalDbConstants.COLLECTION)

@app.route('/')
def index():
    variable_keys, variable_labels = VariableConstants.get_logged_variable_list()
    hospital_names = RopodAdminQueries.get_hospital_names(local_db_connection)
    return render_template('index.html', hospitals=hospital_names, variable_keys=variable_keys, variable_labels=variable_labels)

@app.route('/get_hospital_ips', methods=['GET', 'POST'])
def get_hospital_ips():
    hospital = request.args.get('hospital', '', type=str)
    ips = RopodAdminQueries.get_hospital_black_box_ips(local_db_connection, hospital)
    return jsonify(ips=ips)

@app.route('/get_data', methods=['GET', 'POST'])
def get_data():
    variable = request.args.get('variable', '', type=str)
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    db_server_ip = request.args.get('server_ip', '', type=str)

    db_connection = DbConnection(db_server_ip, DbConstants.DATABASE, DbConstants.COLLECTION)

    start_date_components = start_date.split('/')
    end_date_components = end_date.split('/')

    start_time = datetime(int(start_date_components[2]), int(start_date_components[0]), int(start_date_components[1]))
    end_time = datetime(int(end_date_components[2]), int(end_date_components[0]), int(end_date_components[1]))

    start_timestamp = (start_time - datetime(1970, 1, 1)).total_seconds() * 1000
    end_timestamp = (end_time - datetime(1970, 1, 1)).total_seconds() * 1000

    data, data_labels = DbQueries.get_data(db_connection, variable, start_timestamp, end_timestamp)
    return jsonify(data=data, data_labels=data_labels)

@app.route('/add_ropod')
def add_ropod():
    hospital_names = RopodAdminQueries.get_hospital_names(local_db_connection)
    return render_template('ropod_crud/add_ropod.html', hospitals=hospital_names)

@app.route('/add_new_ropod', methods=['POST'])
def add_new_ropod():
    data = request.get_json(force=True)
    hospital = data['hospital']
    ip_address = data['ip_address']
    RopodAdminQueries.add_new_ropod(local_db_connection, hospital, ip_address)
    return jsonify(success=True)

@app.route('/update_ropod')
def update_ropod():
    hospital_names = RopodAdminQueries.get_hospital_names(local_db_connection)
    return render_template('ropod_crud/update_ropod.html', hospitals=hospital_names)

@app.route('/update_existing_ropod', methods=['POST'])
def update_existing_ropod():
    data = request.get_json(force=True)
    old_hospital = data['old_hospital']
    old_ip_address = data['old_ip_address']
    new_hospital = data['new_hospital']
    new_ip_address = data['new_ip_address']
    RopodAdminQueries.update_existing_ropod(local_db_connection, old_hospital, old_ip_address, new_hospital, new_ip_address)
    return jsonify(success=True)

@app.route('/delete_ropod')
def delete_ropod():
    hospital_names = RopodAdminQueries.get_hospital_names(local_db_connection)
    return render_template('ropod_crud/delete_ropod.html', hospitals=hospital_names)

@app.route('/remove_ropod', methods=['POST'])
def remove_ropod():
    data = request.get_json(force=True)
    hospital = data['hospital']
    ip_address = data['ip_address']
    RopodAdminQueries.remove_ropod(local_db_connection, hospital, ip_address)
    return jsonify(success=True)

if __name__ == '__main__':
    app.run()
