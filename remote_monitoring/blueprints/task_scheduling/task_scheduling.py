from __future__ import print_function
import uuid
import threading
import math

from flask import Blueprint, jsonify, render_template, request, session
from flask_socketio import emit

from remote_monitoring.common import msg_data, Config, socketio

status_thread = None
status_thread_lock = threading.Lock()

def create_blueprint(communicator):
    task_scheduling = Blueprint('task_scheduling', __name__)
    zyre_communicator = communicator
    config = Config()

    @task_scheduling.route('/schedule_task')
    def run_experiment():
        session['uid'] = uuid.uuid4()
        return render_template('schedule_task.html')

    @task_scheduling.route('/task/get_locations')
    def get_locations():
        locations = [{'name': 'ALP-AKH, Standard-Abladepunkt', 'id': 'pickup_location'},
                     {'name': 'AKH934500, Ward 45, Room 14', 'id': 'delivery_location'}]
        return jsonify(locations=locations, message='')

    @task_scheduling.route('/task/get_device_types')
    def get_device_types():
        device_types = [{'name': 'Mobidik cart', 'id': 'mobidik'}]
        return jsonify(device_types=device_types, message='')

    @task_scheduling.route('/task/send_task_request', methods=['POST'])
    def send_task_request():
        data = request.get_json()
        user_id = data.get('user_id')
        pickup_location = data.get('pickup_location')
        delivery_location = data.get('delivery_location')
        pickup_location_level = int(data.get('pickup_location_level'))
        delivery_location_level = int(data.get('delivery_location_level'))
        device_type = data.get('device_type')

        request_msg = dict(msg_data)
        request_msg['header']['type'] = "TASK-REQUEST"
        request_msg['payload']['userId'] = user_id
        request_msg['payload']['pickupLocation'] = pickup_location
        request_msg['payload']['deliveryLocation'] = delivery_location
        request_msg['payload']['pickupLocationLevel'] = pickup_location_level
        request_msg['payload']['deliveryLocationLevel'] = delivery_location_level
        request_msg['payload']['deviceType'] = device_type

        # where do we get the ID from?
        request_msg['payload']['deviceId'] = '1234567890'
        zyre_communicator.shout(request_msg)
        return jsonify(message='')

    @socketio.on('connect', namespace='/task_scheduling')
    def on_connect():
        robots = config.get_robots()
        global status_thread
        with status_thread_lock:
            if status_thread is None:
                status_thread = socketio.start_background_task(target=emit_robot_pose,
                                                               robot_ids=robots)

    def emit_robot_pose(robot_ids):
        while True:
            robot_pose_msg_list = list()
            for robot in robot_ids:
                msg = zyre_communicator.get_pose(robot)
                robot_pose_msg = dict()
                if msg:
                    robot_pose_msg['robotId'] = msg['payload']['robotId']
                    robot_pose_msg['x'] = msg['payload']['pose']['x']
                    robot_pose_msg['y'] = msg['payload']['pose']['y']
                    robot_pose_msg['theta'] = msg['payload']['pose']['theta']
                    t1 = float(msg['payload']['pose']['theta']) + (9*math.pi/10.0)
                    t2 = float(msg['payload']['pose']['theta']) - (9*math.pi/10.0)
                    robot_pose_msg['line1x'] = msg['payload']['pose']['x'] + 2*math.cos(t1)
                    robot_pose_msg['line1y'] = msg['payload']['pose']['y'] + 2*math.sin(t1)
                    robot_pose_msg['line2x'] = msg['payload']['pose']['x'] + 2*math.cos(t2)
                    robot_pose_msg['line2y'] = msg['payload']['pose']['y'] + 2*math.sin(t2)
                    robot_pose_msg['timestamp'] = msg['header']['timestamp']
                    robot_pose_msg_list.append(robot_pose_msg)
            if robot_pose_msg_list:
                socketio.emit('robot_pose', robot_pose_msg_list, namespace='/task_scheduling')
            socketio.sleep(1.0)

    return task_scheduling

