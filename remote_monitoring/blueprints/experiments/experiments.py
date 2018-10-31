from __future__ import print_function
import uuid

from flask import Blueprint, jsonify, render_template, request, session
from remote_monitoring.common import msg_data, Config

def create_blueprint(communicator):
    experiments = Blueprint('experiments', __name__)
    zyre_communicator = communicator
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

    @experiments.route('/send_experiment_request', methods=['GET', 'POST'])
    def send_experiment_request():
        ropod_id = request.args.get('ropod_id', '', type=str)
        experiment = request.args.get('experiment', '', type=str)

        msg = dict(msg_data)
        msg['header']['type'] = 'ROBOT-EXPERIMENT-REQUEST'
        msg['payload']['userId'] = session['uid'].hex
        msg['payload']['robotId'] = ropod_id
        msg['payload']['experimentType'] = experiment

        client_feedback_msg = ''
        try:
            zyre_communicator.shout(msg)
        except Exception as exc:
            print('[send_experiment_request] %s' % str(exc))
            client_feedback_msg = 'Command could not be sent'
        return jsonify(success=True, message=client_feedback_msg)

    return experiments
