#!/usr/bin/env python

import os
from flask import send_from_directory
from flask import Flask, jsonify, render_template, request, redirect, url_for
# from datetime import datetime
from calendar import datetime

from constants import LocalDbConstants, DbConstants, VariableConstants
from db import DbConnection, DbQueries
from local_db import RopodAdminQueries

import pyre
from pyre import Pyre
from pyre import zhelper
import zmq
import uuid
import logging
import sys
import json
import time

node = Pyre("sender_node")
node.join("CHAT")
node.start()

nodes_list = dict()

t = time.localtime()
current_time = str(t[0])+"-"+str(t[1])+"-"+str(t[2])+"T"+str(t[3])+":"+str(t[4])+":"+str(t[5])+"Z"

features_list = ['robotID', 'sensors', 'timestamp']
start_query_time = "2017-12-10 3:55:40"
end_query_time = "2017-12-10 11:25:40"

msg_data = {
  "header": {
    "type": "CMD",
    "version": "0.1.0",
    "metamodel": "ropod-msg-schema.json",
    "msg_id": "0d05d0bc-f1d2-4355-bd88-edf44e2475c8",
    "timestamp": current_time
  },
  "payload": {
    "metamodel": "ropod-demo-cmd-schema.json",
    "commandList":[
      { 
        "command": "GETQUERY",
        "features": features_list,
        "start_time": start_query_time, 
        "end_time": end_query_time
      }
     ]
  }
}

msg_name_request = 'NameRequest'
dest_name = "receiver_node"
get_info = True
get_queries = True
send_next_query = False
k = 0
q = 0

rec1 = {
    'timestamp': datetime.datetime.strptime('2017-12-10 3:25:40', "%Y-%m-%d %H:%M:%S"),
    'robotID':'r1',
    'pose':'5,8',
    'busy':'y',
    'battery':'51',
    'sensors':[{
        'IR':'1',
        'sonar':'0',
        'laser':'1',
        'microphone':'0'
    }],
    'motor values':[
    {
        'motor1':'8',
        'motor2':'9',
        'motor3':'9',
        'motor4':'8'
    }]
}
rec2 = {
    'timestamp': datetime.datetime.strptime('2017-12-10 4:25:40', "%Y-%m-%d %H:%M:%S"),
    'robotID':'r2',
    'pose':'0,0',
    'busy':'n',
    'battery':'85',
    'sensors':[{
        'IR':'1',
        'sonar':'1',
        'laser':'1',
        'microphone':'0'
    }],
    'motor values':[
    {
        'motor1':'7',
        'motor2':'5',
        'motor3':'5',
        'motor4':'8'
    }]
}


app = Flask(__name__)
local_db_connection = DbConnection('127.0.0.1', LocalDbConstants.DATABASE, LocalDbConstants.COLLECTION)
rid = str()

@app.route('/')
def index():
    variable_keys, variable_labels = VariableConstants.get_logged_variable_list()
    hospitals, ids, ip_addresses = RopodAdminQueries.get_all_ropods(local_db_connection)
    return render_template('index.html', hospitals=hospitals, variable_keys=variable_keys, variable_labels=variable_labels,ids=ids, ip_addresses=ip_addresses)

@app.route('/2')
def index2():
    variable_keys, variable_labels = VariableConstants.get_logged_variable_list()
    hospital_names = RopodAdminQueries.get_hospital_names(local_db_connection)
    return render_template('index.html', hospitals=hospital_names, variable_keys=variable_keys, variable_labels=variable_labels)

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
    return render_template('manage_ropods.html', hospitals=hospitals, ids=ids, ip_addresses=ip_addresses)

@app.route('/get_ropod_features', methods=['GET','POST'])
def get_ropod_features():
    ropod_id = request.args.get('ropod_id','', type=str)
    features = ['Motors','Pose','Sensors','Battery']
    # features_list = request.args.get('features_list', '', type=str)
    return jsonify(ropod_features = features)

@app.route('/get_ropod_features2', methods=['GET','POST'])
def get_ropod_features2():
    ropod_id = request.args.get('ropod_id','', type=str)
    old_time = time.time() # the start time for counting how much time has passed since the start of the query

    n.shout("CHAT", msg_name_request.encode('utf-8'))
    while True:
        if time.time() - old_time > 20:
            break
        rec_msg = node.recv()
        msg_type = rec_msg[0].decode('utf-8')
        sender_uuid = uuid.UUID(bytes=rec_msg[1])
        sender_name = rec_msg[2].decode('utf-8')
        nodes_list[sender_name] = sender_uuid

    msg_data['payload']['commandList'][0] = {"command": "SENDINFO"}
    jmsg_data = json.dumps(msg_data).encode('utf-8')
    dest_uuid = nodes_list[ropod_id]
    node.whisper(dest_uuid, jmsg_data)
    old_time = time.time()
    while True:
        if time.time() - old_time > 60:
            break
        rec_msg = node.recv()
        msg_type = rec_msg[0].decode('utf-8')
        sender_uuid = uuid.UUID(bytes=rec_msg[1])
        data = rec_msg[-1]
        data = data.decode('utf-8')
        if str(msg_type) == 'SHOUT' or str(msg_type) == 'WHISPER':
            try:
                jdata = json.loads(data)
                if jdata['payload']['answerList'][0]['command'] == "ANSWER" and sender_uuid == dest_uuid:
                    received_answer = jdata['payload']['answerList']
                    break
            except Exception as e:
                pass
    # node.stop()
    features = received_answer
    features = ['Motors','Pose','Sensors','Battery']
    return jsonify(ropod_features = features)

@app.route('/run_experiment')
def run_experiment():
    experiment_list = ['go to','stop','run in square','go to base']
    hospitals, ropod_id, ip_addresses = RopodAdminQueries.get_all_ropods(local_db_connection)

    # ropod_id = RopodAdminQueries.get_hospital_ropod_ids(local_db_connection)
    return render_template('run_experiment.html', experiment_list = experiment_list, ropod_id_list=ropod_id)

@app.route('/exec_expermnt', methods=['GET','POST'])
def exec_expermnt():
    ropod_id = request.args.get('ropod_id','', type=str)
    experiment = request.args.get('experiment','', type=str)

    epermnt_result = 'success'
    return jsonify(epermnt_result = epermnt_result)

@app.route('/exec_expermnt2', methods=['GET','POST'])
def exec_expermnt2():
    ropod_id = request.args.get('ropod_id','', type=str)
    experiment = request.args.get('experiment','', type=str)

    old_time = time.time() # the start time for counting how much time has passed since the start of the query

    n.shout("CHAT", msg_name_request.encode('utf-8'))
    while True:
        if time.time() - old_time > 20:
            break
        rec_msg = node.recv()
        msg_type = rec_msg[0].decode('utf-8')
        sender_uuid = uuid.UUID(bytes=rec_msg[1])
        sender_name = rec_msg[2].decode('utf-8')
        nodes_list[sender_name] = sender_uuid

    msg_data['payload']['commandList'][0] = {"command": "Exec_Experiment",
        "experiment": experiment
        }
    jmsg_data = json.dumps(msg_data).encode('utf-8')
    dest_uuid = nodes_list[ropod_id]
    node.whisper(dest_uuid, jmsg_data)
    old_time = time.time()
    while True:
        if time.time() - old_time > 60:
            break
        rec_msg = node.recv()
        msg_type = rec_msg[0].decode('utf-8')
        sender_uuid = uuid.UUID(bytes=rec_msg[1])
        data = rec_msg[-1]
        data = data.decode('utf-8')
        if str(msg_type) == 'SHOUT' or str(msg_type) == 'WHISPER':
            try:
                jdata = json.loads(data)
                if jdata['payload']['answerList'][0]['command'] == "ANSWER" and sender_uuid == dest_uuid:
                    received_answer = jdata['payload']['answerList']
                    break
            except Exception as e:
                pass
    # node.stop()
    epermnt_result = received_answer
    epermnt_result = 'success'
    return jsonify(epermnt_result = epermnt_result)

@app.route('/ropod_info')
def ropod_info():
    features = ['Motors','Pose','Sensors','Battery','Busy']
    ropod_id = request.args.get('ropod_id', '', type=str)
    return render_template('ropod_info.html', features=features, ropod_id=ropod_id)

@app.route('/ropod_query_result')
def ropod_query_result():
    features_list = ['Motors','Pose','Sensors','Battery','Busy']
    return render_template('ropod_query_result.html', features_list=features_list)

@app.route('/get_ropod_query', methods=['GET','POST'] )
def get_ropod_query():
    ropod_id = request.args.get('ropod_id', '', type=str)
    features_list = request.args.get('features', type=str)
    start_query_time = request.args.get('start_timestamp')
    end_query_time = request.args.get('end_timestamp')

    test_result = 'ropod_id: '+str(ropod_id)+' -- features_list: '+str(features_list)+' -- start_query_time: '+str(start_query_time)+' -- end_query_time: '+str(end_query_time)

    test_result2 = [1, 1, 2, 3, 5, 9]
    # ropod_query_data = 
    # for val in query_results:
    	# jq = json.dumps(val, default=json_util.default)
	# jq2 = json.loads(jq)
	# print(jq2['sensors'][0]['laser'])
    return jsonify(query_result = test_result)

@app.route('/get_ropod_query2', methods=['GET','POST'] )
def get_ropod_query2():
    # this is the final method which gets the query from the ropod
    ropod_id = request.args.get('ropod_id', '', type=str)
    features_list = request.args.get('features_list')

    # I have to edit the times as the required format for the query
    start_query_time = request.args.get('start_timestamp')
    end_query_time = request.args.get('end_timestamp')

    # getting the query via pyre
    node.shout("CHAT", msg_name_request.encode('utf-8'))

    old_time = time.time()
    while True:
        if time.time() - old_time > 20:
            break
        rec_msg = n.recv()
        msg_type = rec_msg[0].decode('utf-8')
        sender_uuid = uuid.UUID(bytes=rec_msg[1])
        sender_name = rec_msg[2].decode('utf-8')
        nodes_list[sender_name] = sender_uuid

    msg_data['payload']['commandList'][0] = {"command": "GETQUERY",
        "features": features_list,
        "start_time": start_query_time,
        "end_time": end_query_time
        }
    jmsg_data = json.dumps(msg_data).encode('utf-8')
    dest_uuid = nodes_list[ropod_id]
    node.whisper(dest_uuid, jmsg_data)

    old_time = time.time()
    while True:
        if time.time() - old_time > 20:
            break
        rec_msg = node.recv()
        msg_type = rec_msg[0].decode('utf-8')
        sender_uuid = uuid.UUID(bytes=rec_msg[1])
        data = rec_msg[-1]
        data = data.decode('utf-8')
        if str(msg_type) == 'SHOUT' or str(msg_type) == 'WHISPER':
            try:
                jdata = json.loads(data)
                if jdata['payload']['answerList'][0]['command'] == "ANSWER" and sender_uuid == dest_uuid:
                    received_answer = jdata['payload']['answerList']
                    break
            except Exception as e:
                pass
    # node.stop()
    features_and_vals = received_answer

    # prepare the query result
    # the query result is a dict with keys that are the desired features 
    # and values that are a list of values for each feature and we use
    # this list for plotting
    query_result = dict()
    # ropod_query_data = 
    # for val in query_results:
    	# jq = json.dumps(val, default=json_util.default)
	    # jq2 = json.loads(jq)
	    # print(jq2['sensors'][0]['laser'])
    return jsonify(query_result)
    # return render_template('ropod_query_result.html', features_list=features_list, ropod_id=ropod_id, ropod_query_data=ropod_query_data)

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
    return render_template('edit_ropod.html', hospitals=hospital_names, original_hospital=original_hospital, original_id=original_id, original_ip_address=original_ip_address)

@app.route('/update_existing_ropod', methods=['POST'])
def update_existing_ropod():
    data = request.get_json(force=True)
    old_hospital = data['old_hospital']
    old_id = data['old_id']
    old_ip_address = data['old_ip_address']
    new_hospital = data['new_hospital']
    new_id = data['new_id']
    new_ip_address = data['new_ip_address']
    RopodAdminQueries.update_existing_ropod(local_db_connection, old_hospital, old_id, old_ip_address, new_hospital, new_id, new_ip_address)
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
