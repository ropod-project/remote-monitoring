from __future__ import print_function
from flask import Blueprint, jsonify, render_template, request, session

import ast
import json
import uuid

from remote_monitoring.common import msg_data, communicate_zmq

experiments = Blueprint('experiments', __name__)

@experiments.route('/run_experiment')
def run_experiment():
    session['uid'] = uuid.uuid4()
    return render_template('run_experiment.html')

@experiments.route('/get_ropod_ids', methods=['GET'])
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

@experiments.route('/send_experiment_request', methods=['GET','POST'])
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
