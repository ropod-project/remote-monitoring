from __future__ import print_function
from flask import Blueprint, jsonify, render_template, request, session, send_file

import ast
import json
import uuid

from remote_monitoring.common import msg_data, communicate_zmq

black_box = Blueprint('black_box', __name__)
query_result_file_path = '/tmp/ropod_query_data.json'

@black_box.route('/')
def index():
    session['uid'] = uuid.uuid4()
    return render_template('index.html')

@black_box.route('/get_blackbox_ids', methods=['GET', 'POST'])
def get_blackbox_ids():
    msg = dict(msg_data)
    msg['header']['type'] = "NAME_QUERY"
    msg['payload']['senderId'] = session['uid'].hex
    communication_command = "GET_QUERY_INTERFACE_LIST"
    msg_data_string = json.dumps(msg)
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

@black_box.route('/get_ropod_variables', methods=['GET','POST'])
def get_ropod_variables():
    ropod_id = request.args.get('ropod_id', '', type=str)

    msg = dict(msg_data)
    msg['header']['type'] = "VARIABLE_QUERY"
    msg['payload']['senderId'] = session['uid'].hex
    msg['payload']['ropodId'] = ropod_id

    # communicate_zmq
    msg_data_string = json.dumps(msg)
    communication_command = "VARIABLE_QUERY"
    data = communication_command + '++' + msg_data_string

    variables = list()
    message = ''
    try:
        reply = communicate_zmq(data)
        jreply = json.loads(reply.decode('utf8'))
        for interface in jreply['payload']['variableList']:
            values = list(interface.values())
            if values is not None and values[0] is not None:
                for element in values[0]:
                    variables.append(element)
    # except Exception, exc:
    except Exception as exc:
        print('[get_ropod_variables] %s' % str(exc))
        message = 'Variable list could not be retrieved'
    return jsonify(ropod_variables=variables, message=message)

@black_box.route('/get_ropod_data', methods=['GET','POST'] )
def get_ropod_data():
    ropod_id = request.args.get('ropod_id', '', type=str)
    variable_list = request.args.get('variables').split(',')

    start_query_time = request.args.get('start_timestamp')
    end_query_time = request.args.get('end_timestamp')

    msg = dict(msg_data)
    msg['header']['type'] = "DATA_QUERY"
    msg['payload']['senderId'] = session['uid'].hex
    msg['payload']['ropodId'] = ropod_id
    msg['payload']['variables'] = variable_list
    msg['payload']['startTime'] = start_query_time
    msg['payload']['endTime'] = end_query_time

    communication_command = "DATA_QUERY"
    msg_data_string = json.dumps(msg)
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

@black_box.route('/get_download_query', methods=['GET', 'POST'])
def get_download_query():
    """Responds to a data download query by sending a query to the appropriate
    black box and then saving the data to a temporary file for download.
    """
    ropod_id = request.args.get('ropod_id', '', type=str)
    variable_list = request.args.get('variables').split(',')

    start_query_time = request.args.get('start_timestamp')
    end_query_time = request.args.get('end_timestamp')

    msg = dict(msg_data)
    msg['header']['type'] = "DATA_QUERY"
    msg['payload']['senderId'] = session['uid'].hex
    msg['payload']['ropodId'] = ropod_id
    msg['payload']['variables'] = variable_list
    msg['payload']['startTime'] = start_query_time
    msg['payload']['endTime'] = end_query_time

    communication_command = "DATA_QUERY"
    msg_data_string = json.dumps(msg)
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

@black_box.route('/send_download_file', methods=['GET','POST'])
def send_download_file():
    """Sends a stored data file for download.
    """
    try:
        return send_file(query_result_file_path,
                         as_attachment=True,
                         attachment_filename='ropod_query_result.json')
    except Exception as exc:
        print('[send_download_file] %s' % str(exc))
        message = 'File could not be sent'
        return jsonify(message=message)
