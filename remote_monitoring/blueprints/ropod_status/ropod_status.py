from __future__ import print_function
from flask import Blueprint, jsonify, render_template, request, session
from flask_socketio import emit
from pymongo import MongoClient

import ast
import json
import uuid

from remote_monitoring.common import msg_data, communicate_zmq, socketio

from pyre_communicator.base_class import PyreBaseCommunicator
from threading import Lock
from Queue import LifoQueue


ropod_status = Blueprint('ropod_status', __name__)
ropod_id_list = list()      # for storing the list of ropods (Ropod info page)
ropod_status_list = dict()  # for storing the status reply for each ropod

thread = None
thread_lock = Lock()

client = MongoClient()

status_msg_queues = {}

class PyreTalker(PyreBaseCommunicator):
    def __init__(self, node_name, groups, message_types, verbose=False,
                 interface=None, acknowledge=False):
        super(PyreTalker, self).__init__(node_name, groups, message_types,
                                        verbose=verbose, interface=interface, acknowledge=acknowledge)

    def receive_event_cb(self, zyre_msg):
        if (zyre_msg.msg_type == "SHOUT"):
            peer_name = zyre_msg.peer_name
            if not peer_name in status_msg_queues.keys():
                return
            msg = zyre_msg.msg_content
            try:
                json_msg = json.loads(msg)
            except:
                return
            if "header" in json_msg and "type" in json_msg["header"]:
                if json_msg["header"]["type"] == "HEALTH-STATUS":
                    status_msg_queues[peer_name].put(msg)


@ropod_status.route('/ropod_info')
def ropod_info():
    session['uid'] = uuid.uuid4()
    return render_template('ropod_info.html')

@ropod_status.route('/get_ropod_status_ids', methods=['GET'])
def get_ropod_status_ids():
    msg_data['header']['type'] = "HEALTH-STATUS-NAME-QUERY"
    msg_data['payload']['senderId'] = session['uid'].hex
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
    return True
    ropod_overall_status = True
    ropod_id = ropod_status['payload']['ropodId']
    monitors = ropod_status['payload']['monitors']

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

def get_deployed_ropods():
    cursor = client.deployed_ropods.ropods.find()
    ropods = []
    for r in cursor:
        ropods.append(r['ropod_name'])
    return ropods

def get_deployed_black_boxes():
    cursor = client.deployed_ropods.black_boxes.find()
    black_boxes = []
    for b in cursor:
        black_boxes.append(b)
    return black_boxes


def background_thread():
    pyre = PyreTalker("ropod_status_listener", ['MONITOR'], [], verbose=False)
    socketio.sleep(1)
    while True:
        peers = pyre.peers()
        peers_list = []
        # find all component monitor peers and create
        # queues for their status messages
        for p in peers:
            if p in pyre.peer_directory.keys():
                peer_name = pyre.peer_directory[p]
                # TODO: only look for component monitor peers
                if peer_name not in status_msg_queues.keys():
                    status_msg_queues[peer_name] = LifoQueue()
                peers_list.append(peer_name)
        # emit the health-status message for all ropods
        for key in status_msg_queues.keys():
            try:
                msg = status_msg_queues[key].get(block=False)
                socketio.emit('status_msg', {'data': msg}, namespace='/ropod_status')
            except:
                pass
            # TODO: clear the queues once in a while

        # emit names of all ropods with component monitors
        socketio.emit('zyre_peers', {'data':json.dumps(peers_list)}, namespace='/ropod_status')
        socketio.sleep(1)


@socketio.on('connect', namespace='/ropod_status')
def on_connect():
    ropods = get_deployed_ropods()
    emit('deployed_ropods', {'data':json.dumps(ropods)})

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)

