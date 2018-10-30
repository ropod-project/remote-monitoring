from __future__ import print_function
import json
import uuid

from flask import Blueprint, jsonify, render_template, request, session
from remote_monitoring.common import msg_data, communicate_zmq, Config

experiments = Blueprint('experiments', __name__)
config = Config()

@experiments.route('/run_experiment')
def run_experiment():
    session['uid'] = uuid.uuid4()
    return render_template('run_experiment.html')

@experiments.route('/get_robot_ids', methods=['GET'])
def get_robot_ids():
    robots = list()
    feedback_msg = ''
    try:
        robots = config.get_robots()
    except Exception as exc:
        print('[get_robot_ids] %s' % str(exc))
        feedback_msg = 'An error occurred while retrieving the robot IDs'
    return jsonify(robot_ids=robots, message=feedback_msg)

@experiments.route('/send_experiment_request', methods=['GET','POST'])
def send_experiment_request():
    ropod_id = request.args.get('ropod_id', '', type=str)
    experiment = request.args.get('experiment', '', type=str)

    msg_data['header']['type'] = 'ROBOT-EXPERIMENT-REQUEST'
    msg_data['payload']['userId'] = session['uid'].hex
    msg_data['payload']['robotId'] = ropod_id
    msg_data['payload']['experimentType'] = experiment

    message = ''
    try:
        communication_command = "EXPERIMENT"
        msg_data_string = json.dumps(msg_data)
        data = communication_command + "++" + msg_data_string
        _ = communicate_zmq(data)
    except Exception as exc:
        print('[send_experiment_request] %s' % str(exc))
        message = 'Command could not be sent'
    return jsonify(success=True, message=message)
