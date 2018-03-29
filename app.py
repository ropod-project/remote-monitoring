#!/usr/bin/env python

from __future__ import print_function
import ast
from flask import Flask, jsonify, render_template, request, session

from constants import LocalDbConstants, DbConstants, VariableConstants
from db import DbConnection, DbQueries
from local_db import RopodAdminQueries

import zmq
import json
import uuid

from flask import send_file
from flask import Response

from io import BytesIO

from os.path import expanduser
from gevent.wsgi import WSGIServer


# Initializations
context = zmq.Context()
port = "5670"

msg_data = {
    "header":
    {
        "type": "VARIABLE_QUERY",
        "version": "0.1.0",
        "metamodel": "ropod-msg-schema.json",
        "msg_id": "0d05d0bc-f1d2-4355-bd88-edf44e2475c8",
        "timestamp": ""
    },
    "payload":
    {
        "metamodel": "ropod-demo-cmd-schema.json",
        "commandList":
        [
            {
                "features": [],
                "start_time": "",
                "end_time": ""
            }
        ]
    }
}

ropod_status_msg = {
    "header":
    {
        "type": "STATUS",
        "version": "0.1.0",
        "metamodel": "ropod-msg-schema.json",
        "msg_id": "0d05d0bc-f1d2-4355-bd88-edf44e2475c8",
        "timestamp": ""
    },
    "payload":
    {
        "metamodel": "ropod-status-schema.json",
        "status":
        {
            "hardware_devices":
            {
                "battery": 56.4,
                "motors_on": True,
                "wheel1": True,
                "wheel2": True,
                "wheel3": True,
                "wheel4": False,
                "wifi": 89
            },
            "sensors":
            {
                "joypad": False,
                "laser_front": True,
                "laser_back": True
            },
            "software":
            {
                "ros_master": True,
                "ros_nodes":
                {
                    "node_1": False,
                    "node_n": True
                },
                "localised": True,
                "laser_map_matching": 66.5
            }
        }
    }
}

def communicate_zmq(data):
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:%s" % port)
    socket.send(data.encode('ascii'))
    reply = socket.recv()
    return reply

################ Flask codes #############################

ropod_id_list = list()      # for storing the list of ropods (Ropod info page)
ropod_status_list = dict()  # for storing the status reply for each ropod

# the path and file name for storing the query result for downloading data
query_result_file_path = '/tmp/ropod_query_data.json'


app = Flask(__name__)
local_db_connection = DbConnection('127.0.0.1', LocalDbConstants.DATABASE, LocalDbConstants.COLLECTION)

################ Black box data interface ################
@app.route('/')
def index():
    session['uid'] = uuid.uuid4()
    return render_template('index.html')

@app.route('/get_blackbox_ids', methods=['GET', 'POST'])
def get_blackbox_ids():
    msg_data['header']['type'] = "NAME_QUERY"
    msg_data['payload']['sender_id'] = session['uid'].hex
    communication_command = "GET_QUERY_INTERFACE_LIST"
    msg_data_string = json.dumps(msg_data)
    data = communication_command + "++" + msg_data_string

    ropod_ids = dict()
    message = ''
    try:
        query_reply = communicate_zmq(data)
        if query_reply:
            ropods = ast.literal_eval(query_reply.decode('ascii'))
            ropod_ids = []
            for node in ropods:
                sender_name = node[0]
                suffix_idx = sender_name.find('_query_interface')
                ropod_ids.append(sender_name[0:suffix_idx])
    # except Exception, exc:
    except Exception as exc:
        print('[get_blackbox_ids] %s' % str(exc))
        message = 'Black box list could not be retrieved'
    return jsonify(ids=ropod_ids, message=message)

@app.route('/get_ropod_features', methods=['GET','POST'])
def get_ropod_features():
    ropod_id = request.args.get('ropod_id', '', type=str)

    msg_data['header']['type'] = "VARIABLE_QUERY"
    msg_data['payload']['sender_id'] = session['uid'].hex
    msg_data['payload']['ropod_id'] = ropod_id
    msg_data['payload']['commandList'][0] = {"command": "GET_ROPOD_FEATURES"}

    # communicate_zmq
    msg_data_string = json.dumps(msg_data)
    communication_command = "VARIABLE_QUERY"
    data = communication_command + '++' + msg_data_string

    features = list()
    message = ''
    try:
        reply = communicate_zmq(data)
        jreply = json.loads(reply.decode('utf8'))
        for interface in jreply['payload']['variableList']:
            values = list(interface.values())
            if values is not None and values[0] is not None:
                for element in values[0]:
                    features.append(element)
    # except Exception, exc:
    except Exception as exc:
        print('[get_ropod_features] %s' % str(exc))
        message = 'Feature list could not be retrieved'
    return jsonify(ropod_features=features, message=message)

@app.route('/get_ropod_data', methods=['GET','POST'] )
def get_ropod_data():
    ropod_id = request.args.get('ropod_id', '', type=str)
    feature_list = request.args.get('features').split(',')

    start_query_time = request.args.get('start_timestamp')
    end_query_time = request.args.get('end_timestamp')

    msg_data['header']['type'] = "DATA_QUERY"
    msg_data['payload']['sender_id'] = session['uid'].hex
    msg_data['payload']['ropod_id'] = ropod_id
    msg_data['payload']['commandList'][0] = {"features": feature_list,
                                             "start_time": start_query_time,
                                             "end_time": end_query_time}

    communication_command = "DATA_QUERY"
    msg_data_string = json.dumps(msg_data)
    data_query = communication_command + "++" + msg_data_string

    variables = list()
    data = list()
    message = ''
    try:
        query_reply = communicate_zmq(data_query)
        query_reply_json = json.loads(query_reply.decode('utf8'))
        query_result = query_reply_json['payload']['dataList']
        if query_result is not None and query_result[0] is not None:
            for data_dict in query_result:
                for key, value in data_dict.items():
                    variables.append(key)
                    variable_data_list = list()
                    for item in value:
                        variable_data_list.append(ast.literal_eval(item))
                    data.append(variable_data_list)
    # except Exception, exc:
    except Exception as exc:
        print('[get_ropod_data] %s' % str(exc))
        message = 'Data could not be retrieved'
    return jsonify(variables=variables, data=data, message=message)

@app.route('/get_download_query', methods=['GET', 'POST'])
def get_download_query():
    """Method for getting data query for download.
    This method gets a query from the blackbox and store it in a file and returns a success response to ajax
    """
    ropod_id = request.args.get('ropod_id', '', type=str)
    feature_list = request.args.get('features').split(',')

    start_query_time = request.args.get('start_timestamp')
    end_query_time = request.args.get('end_timestamp')

    msg_data['header']['type'] = "DATA_QUERY"
    msg_data['payload']['sender_id'] = session['uid'].hex
    msg_data['payload']['ropod_id'] = ropod_id
    msg_data['payload']['commandList'][0] = {"features": feature_list,
                                             "start_time": start_query_time,
                                             "end_time": end_query_time}

    communication_command = "DATA_QUERY"
    msg_data_string = json.dumps(msg_data)
    data = communication_command + "++" + msg_data_string

    message = ''
    try:
        query_reply = communicate_zmq(data)
        query_reply_json = json.loads(query_reply.decode('utf8'))

        with open(query_result_file_path, 'w') as download_file:
            json.dump(query_reply_json, download_file)
        return jsonify(success=True)
    # except Exception, exc:
    except Exception as exc:
        print('[get_download_query_ropod_data] %s' % str(exc))
        message = 'Data could not be retrieved'
        return jsonify(message=message)

@app.route('/send_download_file', methods=['GET','POST'])
def send_download_file():
    """This method sends the stored query result to the client for download
    """
    try:
        return send_file(query_result_file_path, as_attachment=True, attachment_filename='ropod_query_result.json')
    except Exception as exc:
        print('[send_download_file_ropod_data] %s' % str(exc))
        message = 'File could not be sent'
        return jsonify(message=message)

##########################################################


################ Experiment request interface ################
@app.route('/run_experiment')
def run_experiment():
    session['uid'] = uuid.uuid4()
    return render_template('run_experiment.html')

@app.route('/get_ropod_ids', methods=['GET'])
def get_ropod_ids():
    msg_data['header']['type'] = "NAME_QUERY"
    msg_data['payload']['sender_id'] = session['uid'].hex
    communication_command = "GET_ROPOD_LIST"
    msg_data_string = json.dumps(msg_data)
    data = communication_command + "++" + msg_data_string

    ropod_ids = dict()
    message = ''
    try:
        query_reply = communicate_zmq(data)
        if query_reply:
            ropods = ast.literal_eval(query_reply.decode('ascii'))
            ropod_ids = []
            for node in ropods:
                sender_name = node[0]
                suffix_idx = sender_name.find('_query_interface')
                ropod_ids.append(sender_name[0:suffix_idx])
    # except Exception, exc:
    except Exception as exc:
        print('[get_ropod_ids] %s' % str(exc))
        message = 'Ropod list could not be retrieved'
    return jsonify(ropod_ids=ropod_ids, message=message)

@app.route('/send_experiment_request', methods=['GET','POST'])
def send_experiment_request():
    ropod_id = request.args.get('ropod_id', '', type=str)
    experiment = request.args.get('experiment', '', type=str)

    msg_data['header']['type'] = "RUN_EXPERIMENT"
    msg_data['payload']['sender_id'] = session['uid'].hex
    msg_data['payload']['ropod_id'] = ropod_id
    msg_data['payload']['experiment'] = experiment

    message = ''
    try:
        communication_command = "DATA_QUERY"
        msg_data_string = json.dumps(msg_data)
        data = communication_command + "++" + msg_data_string
        _ = communicate_zmq(data)
    # except Exception, exc:
    except Exception as exc:
        print('[send_experiment_request] %s' % str(exc))
        message = 'Command could not be sent'
    return jsonify(success=True, message=message)
##########################################################


################ Ropod status interface ##################
@app.route('/ropod_info')
def ropod_info():
    session['uid'] = uuid.uuid4()
    return render_template('ropod_info.html')

@app.route('/get_ropod_status_ids', methods=['GET'])
def get_ropod_status_ids():
    msg_data['header']['type'] = "STATUS_NAME_QUERY"
    msg_data['payload']['sender_id'] = session['uid'].hex
    communication_command = "GET_ROPOD_IDs"
    msg_data_string = json.dumps(msg_data)
    data = communication_command + "++" + msg_data_string

    message = ''
    try:
        query_reply = communicate_zmq(data)
        if query_reply:
            ropods = ast.literal_eval(query_reply.decode('ascii'))
            for node in ropods:
                sender_name = node[0]
                ropod_id_list.append(sender_name)
    # except Exception, exc:
    except Exception as exc:
        print('[get_ropod_status_ids] %s' % str(exc))
        message = 'Ropod list could not be retrieved'
    return jsonify(ropod_ids=ropod_id_list, message=message)

@app.route('/get_status_of_all_ropods', methods=['GET','POST'])
def get_status_of_all_ropods():
    '''Receives a list of ropod_ids and makes a status query
    for each of them, checks the status, and returns the result
    '''

    all_ropods_status = dict()
    message = ''
    try:
        # get ropod_id list
        for ropod in ropod_id_list:
            # get status query for each ropod in a loop
            status_reply = get_one_ropod_status(ropod)

            # transform the result to json and store it into ropod_status_list
            status_reply_json = json.loads(status_reply.decode('utf8'))
            ropod_status_list[ropod] = status_reply_json

            # check the ropod status
            ropod_overall_status = check_ropod_overall_status(status_reply_json)

            # fill and returns a dictionary whose keys are ropod_ids
            # and values are bool reply from check_ropod_overall_status function and timestamp
            status_time = status_reply_json['header']['timestamp']
            all_ropods_status[ropod] = [ropod_overall_status, status_time]

    # except Exception, exc:
    except Exception as exc:
        print('[get_status_of_all_ropods] %s' % str(exc))
        message = 'Status could not be retrieved'
    return jsonify(status_list=all_ropods_status, message=message)

def get_one_ropod_status(ropod_id):
    """Returns a status query for one ropod
    """
    msg_data['header']['type'] = "STATUS"
    msg_data['payload']['sender_id'] = session['uid'].hex
    msg_data['payload']['ropod_id'] = ropod_id

    communication_command = "STATUS_QUERY"
    msg_data_string = json.dumps(msg_data)
    data = communication_command + "++" + msg_data_string
    query_reply = communicate_zmq(data)
    return query_reply

def check_ropod_overall_status(ropod_status):
    """Returns True if, on a given ropod, everything is working and all
    numerical values are above a predefined threshold; returns False otherwise.
    """
    ropod_overall_status = True
    status = ropod_status['payload']['status']

    wifi_threshold = -70
    battery_threshold = 21
    laser_map_threshold = 90

    for category, _ in status.items():
        for variable, value in status[category].items():
            if variable == 'ros_nodes':
                for list_item, item_value in status[category][variable].items():
                    if isinstance(item_value, bool):
                        if not item_value:
                            ropod_overall_status = False
                            break
                    else:
                        if list_item == 'wifi' and item_value < wifi_threshold:
                            ropod_overall_status = False
                            break
                        elif list_item == 'battery' and item_value < battery_threshold:
                            ropod_overall_status = False
                            break
                        elif list_item == 'laser_map_matching' and item_value < laser_map_threshold:
                            ropod_overall_status = False
                            break
            else:
                if isinstance(value, bool):
                    if not value:
                        ropod_overall_status = False
                        break
                else:
                    if variable == 'wifi' and value < wifi_threshold:
                        ropod_overall_status = False
                        break
                    elif variable == 'battery' and value < battery_threshold:
                        ropod_overall_status = False
                        break
                    elif variable == 'laser_map_matching' and value < laser_map_threshold:
                        ropod_overall_status = False
                        break

    return ropod_overall_status

@app.route('/read_ropod_status', methods=['GET', 'POST'])
def read_ropod_status():
    '''Reads the status of a single ropod from 'ropod_status_list'
    '''
    message = ''
    try:
        ropod_id = request.args.get('ropod_id', '', type=str)
        ropod_status = ropod_status_list[ropod_id]
        return jsonify(ropod_status=ropod_status, message=message)
    # except Exception, exc:
    except Exception as exc:
        print('[read_ropod_status] %s' % str(exc))
        message = 'Status could not be retrieved'
        return jsonify(ropod_status=None, message=message)
##########################################################

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

@app.route('/add_ropod')
def add_ropod():
    hospital_names = RopodAdminQueries.get_hospital_names(local_db_connection)
    return render_template('add_ropod.html', hospitals=hospital_names)

@app.route('/add_new_ropod', methods=['POST'])
def add_new_ropod():
    data = request.get_json(force=True)
    hospital = data['hospital']
    ropod_id = data['ropod_id']
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
    try:
        app.secret_key = 'area5142'
        app.config['SESSION_TYPE'] = 'filesystem'
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()
    finally:
        context.term()
