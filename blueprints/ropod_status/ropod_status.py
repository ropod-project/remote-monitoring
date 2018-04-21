from __future__ import print_function
from flask import Blueprint, jsonify, render_template, request, session

import ast
import json
import uuid

from remote_monitoring.common import msg_data, communicate_zmq

ropod_status = Blueprint('ropod_status', __name__)
ropod_id_list = list()      # for storing the list of ropods (Ropod info page)
ropod_status_list = dict()  # for storing the status reply for each ropod

@ropod_status.route('/ropod_info')
def ropod_info():
    session['uid'] = uuid.uuid4()
    return render_template('ropod_info.html')

@ropod_status.route('/get_ropod_status_ids', methods=['GET'])
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

@ropod_status.route('/get_status_of_all_ropods', methods=['GET','POST'])
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

@ropod_status.route('/read_ropod_status', methods=['GET', 'POST'])
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
