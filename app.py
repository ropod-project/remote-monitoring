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

import zmq
import uuid
import logging
import sys
import json
import time


# Initializations
port = "5670"

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
    "timestamp": ""
  },
  "payload": {
    "metamodel": "ropod-demo-cmd-schema.json",
    "commandList":[
      {
        "features": [],
        "start_time": "",
        "end_time": ""
      }
     ]
  }
}

def communicate_zmq(data):
    socket.send(data.encode('ascii'))
    reply = socket.recv()
    return reply

app = Flask(__name__)
local_db_connection = DbConnection('127.0.0.1', LocalDbConstants.DATABASE, LocalDbConstants.COLLECTION)
rid = str()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_ropod_ids', methods=['GET', 'POST'])
def get_ropod_ids():
    msg_data['header']['type'] = "NAME_QUERY"
    communication_command = "GET_ROPOD_LIST"
    msg_data_string = json.dumps(msg_data)
    data = communication_command + "++" + msg_data_string

    ropod_ids = dict()
    query_reply = communicate_zmq(data)
    if query_reply:
        ropods = ast.literal_eval(query_reply.decode('ascii'))
        ropod_ids = []
        for node in ropods:
            sender_name = node[0]
            suffix_idx = sender_name.find('_query_interface')
            ropod_ids.append(sender_name[0:suffix_idx])
    return jsonify(ids=ropod_ids)

@app.route('/get_ropod_features', methods=['GET','POST'])
def get_ropod_features():
    ropod_id = request.args.get('ropod_id', '', type=str)

    msg_data['header']['type'] = "VARIABLE_QUERY"
    msg_data['payload']['ropod_id'] = ropod_id
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

@app.route('/get_ropod_data', methods=['GET','POST'] )
def get_ropod_data():
    ropod_id = request.args.get('ropod_id', '', type=str)
    feature_list = request.args.get('features').split(',')

    start_query_time = request.args.get('start_timestamp')
    end_query_time = request.args.get('end_timestamp')

    msg_data['header']['type'] = "DATA_QUERY"
    msg_data['payload']['ropod_id'] = ropod_id
    msg_data['payload']['commandList'][0] = {"features": feature_list,
                                             "start_time": start_query_time,
                                             "end_time": end_query_time}

    communication_command = "DATA_QUERY"
    msg_data_string = json.dumps(msg_data)
    data = communication_command + "++" + msg_data_string

    query_reply = communicate_zmq(data)
    query_reply_json = json.loads(query_reply.decode('utf8'))

    variables = list()
    data = list()
    query_result = query_reply_json['payload']['dataList']
    if query_result is not None and query_result[0] is not None:
        for data_dict in query_result:
            for key, value in data_dict.iteritems():
                variables.append(key)
                variable_data_list = list()
                for item in value:
                    variable_data_list.append(ast.literal_eval(item))
                data.append(variable_data_list)

    return jsonify(variables=variables, data=data)

@app.route('/download_ropod_data', methods=['GET','POST'] )
def download_ropod_data():
    ropod_id = request.args.get('ropod_id', '', type=str)
    feature_list = request.args.get('features').split(',')

    start_query_time = request.args.get('start_timestamp')
    end_query_time = request.args.get('end_timestamp')

    msg_data['header']['type'] = "DATA_QUERY"
    msg_data['payload']['ropod_id'] = ropod_id
    msg_data['payload']['commandList'][0] = {"features": feature_list,
                                             "start_time": start_query_time,
                                             "end_time": end_query_time}

    communication_command = "DATA_QUERY"
    msg_data_string = json.dumps(msg_data)
    data = communication_command + "++" + msg_data_string

    query_reply = communicate_zmq(data)
    query_reply_json = json.loads(query_reply.decode('utf8'))

    # This is fir extracting the data from the query_result message
    # variables = list()
    # data = list()
    # query_result = query_reply_json['payload']['dataList']
    # if query_result is not None and query_result[0] is not None:
    #     for data_dict in query_result:
    #         for key, value in data_dict.iteritems():
    #             variables.append(key)
    #             variable_data_list = list()
    #             for item in value:
    #                 variable_data_list.append(ast.literal_eval(item))
    #             data.append(variable_data_list)

    # test for downloading the data
    download_path = '~/Download/'

    # save the data
    with open( download_path+'test.csv', 'w') as download_file:
        json.dump(feature_list, download_file)


    # return jsonify(variables=variables, data=data)
    return jsonify(success=True)
    

@app.route('/get_hospital_ropod_ids', methods=['GET', 'POST'])
def get_hospital_ropod_ids():
    hospital = request.args.get('hospital', '', type=str)
    ids = RopodAdminQueries.get_hospital_ropod_ids(local_db_connection, hospital)
    return jsonify(ids=ids)

@app.route('/manage_ropods')
def manage_ropods():
    hospitals, ids, ip_addresses = RopodAdminQueries.get_all_ropods(local_db_connection)
    return render_template('manage_ropods.html', hospitals=hospitals,
                           ids=ids, ip_addresses=ip_addresses)

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
