#!/usr/bin/env python

"""
This is a version for communiating with zmq-mediator

"""

import os
import ast
from flask import send_from_directory
from flask import Flask, jsonify, render_template, request, redirect, url_for
# from datetime import datetime
from calendar import datetime

from constants import LocalDbConstants, DbConstants, VariableConstants
from db import DbConnection, DbQueries
from local_db import RopodAdminQueries

# import pyre
# from pyre import Pyre
# from pyre import zhelper
import zmq
import uuid
import logging
import sys
import json
import time


# Initializations
port = "5670"
msg_name_request = 'NameRequest'

t = time.localtime()
current_time = str(t[0])+"-"+str(t[1])+"-"+str(t[2])+"T"+str(t[3])+":"+str(t[4])+":"+str(t[5])+"Z"

features_list = ['robotID', 'sensors', 'timestamp']
start_query_time = "2017-12-10 3:55:40"
end_query_time = "2017-12-10 11:25:40"

# creating a zmq client using zmq.REQ
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%s" % port)

msg_data = {
  "header": {
    "type": "VARIABLE_QUERY",
    "version": "0.1.0",
    "metamodel": "ropod-msg-schema.json",
    "msg_id": "0d05d0bc-f1d2-4355-bd88-edf44e2475c8",
    "timestamp": current_time
  },
  "payload": {
    "metamodel": "ropod-demo-cmd-schema.json",
    "commandList":[
      {
        # "command": "GETQUERY",
        "features": features_list,
        "start_time": "02/05/2018",
        "end_time": "02/23/2018"
      }
     ]
  }
}


ropod_ids = list()

def communicate_zmq(data):
    # sending data
    socket.send(data.encode('ascii'))
    reply = socket.recv()
    return reply


app = Flask(__name__)
local_db_connection = DbConnection('127.0.0.1', LocalDbConstants.DATABASE, LocalDbConstants.COLLECTION)
rid = str()

@app.route('/')
def index():
    msg_data['header']['type'] = "NAME_QUERY"
    communication_command = "GET_ROPOD_LIST"
    msg_data_string = json.dumps(msg_data)
    data = communication_command + "++" + msg_data_string

    query_reply = communicate_zmq(data)
    if len(query_reply) == 0:
        return render_template('index.html', ids=dict())
    ropods = ast.literal_eval(query_reply.decode('ascii'))

    ropod_ids = []
    for node in ropods:
        sender_name = node[0]
        ropod_ids.append(sender_name)

    return render_template('index.html', ids=ropod_ids)

@app.route('/get_hospital_ropod_ids', methods=['GET', 'POST'])
def get_hospital_ropod_ids():
    hospital = request.args.get('hospital', '', type=str)
    ids = RopodAdminQueries.get_hospital_ropod_ids(local_db_connection, hospital)
    return jsonify(ids=ids)

@app.route('/get_data', methods=['GET', 'POST'])
def get_data():
    variable = request.args.get('variable', '', type=str)
    start_timestamp = request.args.get('start_time', '', type=float)
    end_timestamp = request.args.get('end_time', '', type=float)
    hospital = request.args.get('hospital', '', type=str)
    ropod_id = request.args.get('ropod_id', '', type=str)

    ip_address = RopodAdminQueries.get_black_box_ip(local_db_connection, hospital, ropod_id)
    db_connection = DbConnection(ip_address, DbConstants.DATABASE, DbConstants.COLLECTION)
    data, data_labels = DbQueries.get_data(db_connection, variable, start_timestamp, end_timestamp)
    return jsonify(data=data, data_labels=data_labels)

@app.route('/manage_ropods')
def manage_ropods():
    hospitals, ids, ip_addresses = RopodAdminQueries.get_all_ropods(local_db_connection)
    return render_template('manage_ropods.html', hospitals=hospitals,
                           ids=ids, ip_addresses=ip_addresses)

@app.route('/get_ropod_features', methods=['GET','POST'])
def get_ropod_features():
    ropod_id = request.args.get('ropod_id', '', type=str)
    features_list = request.args.get('features_list', '', type=str)

    msg_data['header']['type'] = "VARIABLE_QUERY"
    msg_data['payload']['commandList'][0] = {"command": "GET_ROPOD_FEATURES"}

    # communicate_zmq
    msg_data_string = json.dumps(msg_data)
    communication_command = "VARIABLE_QUERY"
    data = communication_command + '++' + msg_data_string

    reply = communicate_zmq(data)
    jreply = json.loads(reply.decode('utf8'))

    features = list()
    for interface in jreply['payload']['variableList']:
        values = list(interface.values())
        if values is not None and values[0] is not None:
            for element in values[0]:
                features.append(element)

    return jsonify(ropod_features=features)

@app.route('/exec_expermnt', methods=['GET','POST'])
def exec_expermnt():
    ropod_id = request.args.get('ropod_id', '', type=str)
    experiment = request.args.get('experiment', '', type=str)
    msg_data['payload']['commandList'][0] = {"command": "Exec_Experiment",
                                             "experiment": experiment}

    # communicate_zmq
    msg_data_string = json.dumps(msg_data)
    communication_command = 'EXECUTE_EXPERIMENT'
    data = communication_command + '++' + msg_data_string

    epermnt_result = communicate_zmq(data)

    # prepare the experiment result in the correct format
    return jsonify(epermnt_result=epermnt_result)

@app.route('/run_experiment')
def run_experiment():
    experiment_list = ['go to','stop', 'run in square', 'go to base']
    hospitals, ropod_id, ip_addresses = RopodAdminQueries.get_all_ropods(local_db_connection)

    # ropod_id = RopodAdminQueries.get_hospital_ropod_ids(local_db_connection)
    return render_template('run_experiment.html',
                           experiment_list=experiment_list,
                           ropod_id_list=ropod_id)

@app.route('/ropod_info')
def ropod_info():
    features = ['Motors','Pose','Sensors','Battery','Busy']
    ropod_id = request.args.get('ropod_id', '', type=str)
    return render_template('ropod_info.html', features=features, ropod_id=ropod_id)

@app.route('/get_ropod_data', methods=['GET','POST'] )
def get_ropod_data():
    # this is the final method which gets the query from the ropod
    ropod_id = request.args.get('ropod_id', '', type=str)
    feature_list = request.args.get('features').split(',')

    # I have to edit the times as the required format for the query
    start_query_time = request.args.get('start_timestamp')
    end_query_time = request.args.get('end_timestamp')

    # getting the query via the zmq-mediator
    msg_data['header']['type'] = "DATA_QUERY"
    msg_data['payload']['commandList'][0] = {
        #"features": ["ros_cmd_vel/linear_x", "ros_cmd_vel/linear_y", "ros_cmd_vel/linear_z"],
        "features": feature_list,
        "start_time": "1517236467",
        "end_time": "1520707779"
        }

    communication_command = "DATA_QUERY"
    msg_data_string = json.dumps(msg_data)
    data = communication_command + "++" + msg_data_string

    query_reply = communicate_zmq(data)
    query_reply_json = json.loads(query_reply.decode('utf8'))

    query_result = query_reply_json['payload']['dataList']
    variables = list()
    data = list()
    for data_dict in query_result:
        for key, value in data_dict.iteritems():
            variables.append(key)
            variable_data_list = list()
            for item in value:
                variable_data_list.append(ast.literal_eval(item))
            data.append(variable_data_list)
    return jsonify(variables=variables, data=data)

@app.route('/add_ropod')
def add_ropod():
    hospital_names = RopodAdminQueries.get_hospital_names(local_db_connection)
    return render_template('add_ropod.html', hospitals=hospital_names)

@app.route('/add_new_ropod', methods=['POST'])
def add_new_ropod():
    data = request.get_json(force=True)
    hospital = data['hospital']
    ropod_id = data['ropod_id']
    rid = data['ropod_id']
    ip_address = data['ip_address']
    RopodAdminQueries.add_new_ropod(local_db_connection, hospital, ropod_id, ip_address)
    return jsonify(success=True)

@app.route('/edit_ropod')
def edit_ropod():
    hospital_names = RopodAdminQueries.get_hospital_names(local_db_connection)
    original_hospital = request.args.get('hospital', '', type=str)
    original_id = request.args.get('ropod_id', '', type=str)
    original_ip_address = request.args.get('ip_address', '', type=str)
    return render_template('edit_ropod.html',
                           hospitals=hospital_names,
                           original_hospital=original_hospital,
                           original_id=original_id,
                           original_ip_address=original_ip_address)

@app.route('/update_existing_ropod', methods=['POST'])
def update_existing_ropod():
    data = request.get_json(force=True)
    old_hospital = data['old_hospital']
    old_id = data['old_id']
    old_ip_address = data['old_ip_address']
    new_hospital = data['new_hospital']
    new_id = data['new_id']
    new_ip_address = data['new_ip_address']
    RopodAdminQueries.update_existing_ropod(local_db_connection,
                                            old_hospital, old_id, old_ip_address,
                                            new_hospital, new_id, new_ip_address)
    return jsonify(success=True)

@app.route('/delete_ropod', methods=['POST'])
def delete_ropod():
    data = request.get_json(force=True)
    hospital = data['hospital']
    ropod_id = data['ropod_id']
    ip_address = data['ip_address']
    RopodAdminQueries.delete_ropod(local_db_connection, hospital, ropod_id, ip_address)
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
