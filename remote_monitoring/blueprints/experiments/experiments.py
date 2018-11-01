from __future__ import print_function
import uuid
import threading
import json

from flask import Blueprint, jsonify, render_template, request, session
from remote_monitoring.common import socketio, msg_data, Config

feedback_thread = None
feedback_thread_lock = threading.Lock()

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

    @experiments.route('/get_experiment_list', methods=['GET'])
    def get_experiment_list():
        experiments = dict()
        feedback_msg = ''
        try:
            experiments = config.get_experiments()
        except Exception as exc:
            print('[get_experiment_list] %s' % str(exc))
            feedback_msg = 'An error occurred while retrieving the experiment list'
        return jsonify(experiments=experiments, message=feedback_msg)

    @experiments.route('/send_experiment_request', methods=['GET', 'POST'])
    def send_experiment_request():
        '''Sends a "ROBOT-EXPERIMENT-REQUEST" message to a robot with ID "robot_id"
        for performing the experiment with ID "experiment" (both the robot ID and
        the experiment ID are expected to be passed in the request).
        '''
        robot_id = request.args.get('robot_id', '', type=str)
        experiment = request.args.get('experiment', '', type=str)

        msg = dict(msg_data)
        msg['header']['type'] = 'ROBOT-EXPERIMENT-REQUEST'
        msg['payload']['userId'] = session['uid'].hex
        msg['payload']['robotId'] = robot_id
        msg['payload']['experimentType'] = experiment

        client_feedback_msg = ''
        try:
            zyre_communicator.shout(msg)

            global feedback_thread
            with feedback_thread_lock:
                if not feedback_thread:
                    feedback_thread = socketio.start_background_task(target=get_experiment_feedback,
                                                                     session_id=session['uid'].hex,
                                                                     robot_id=robot_id)
        except Exception as exc:
            print('[send_experiment_request] %s' % str(exc))
            client_feedback_msg = 'Command could not be sent'
        return jsonify(success=True, message=client_feedback_msg)

    def get_experiment_feedback(session_id, robot_id):
        experiment_ongoing = True
        while experiment_ongoing:
            feedback_msg = zyre_communicator.get_experiment_feedback(session_id, robot_id)
            if feedback_msg and feedback_msg['robot_id'] == robot_id:
                if feedback_msg['feedback_type'] == 'ROBOT-COMMAND-FEEDBACK':
                    socketio.emit('experiment_feedback',
                                  json.dumps(feedback_msg),
                                  namespace='/experiments')
                elif feedback_msg['feedback_type'] == 'ROBOT-EXPERIMENT-FEEDBACK':
                    socketio.emit('experiment_feedback',
                                  json.dumps(feedback_msg),
                                  namespace='/experiments')
                    experiment_ongoing = False
                socketio.sleep(0.05)

        global feedback_thread
        feedback_thread = None

    return experiments
