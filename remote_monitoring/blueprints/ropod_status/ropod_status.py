from __future__ import print_function
from flask import Blueprint, jsonify, render_template, request, session
from flask_socketio import emit

import ast
import json
import uuid

from remote_monitoring.common import socketio
from remote_monitoring.common import get_deployed_ropods, get_deployed_black_boxes

from pyre_communicator.base_class import PyreBaseCommunicator
from threading import Lock
from Queue import LifoQueue


ropod_status = Blueprint('ropod_status', __name__)

thread = None
thread_lock = Lock()

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
            # clear the queues once in a while
            if (status_msg_queues[key].qsize() > 5):
                while (status_msg_queues[key].qsize() > 2):
                    status_msg_queues[key].get(block=False)

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

