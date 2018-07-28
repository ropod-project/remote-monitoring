from __future__ import print_function
from flask import Blueprint, jsonify, render_template, request, session

import json
import uuid

from remote_monitoring.common import msg_data, communicate_zmq

task_scheduling = Blueprint('task_scheduling', __name__)

@task_scheduling.route('/schedule_task')
def run_experiment():
    session['uid'] = uuid.uuid4()
    return render_template('schedule_task.html')

@task_scheduling.route('/get_locations')
def get_locations():
    locations = [{'name': 'ALP-AKH, Standard-Abladepunkt', 'id': 'pickup_location'},
                 {'name': 'AKH934500, Ward 45, Room 14', 'id': 'delivery_location'}]
    return jsonify(locations=locations, message='')

@task_scheduling.route('/get_device_types')
def get_device_types():
    device_types = [{'name': 'Mobidik cart', 'id': 'mobidik'}]
    return jsonify(device_types=device_types, message='')

@task_scheduling.route('/send_task_request', methods=['GET','POST'])
def send_task_request():
    data = request.get_json()
    user_id = data.get('user_id')
    pickup_location = data.get('pickup_location')
    delivery_location = data.get('delivery_location')
    pickup_location_level = int(data.get('pickup_location_level'))
    delivery_location_level = int(data.get('delivery_location_level'))
    device_type = data.get('device_type')

    msg_data['header']['type'] = "TASK-REQUEST"
    msg_data['payload']['userId'] = user_id
    msg_data['payload']['pickupLocation'] = pickup_location
    msg_data['payload']['deliveryLocation'] = delivery_location
    msg_data['payload']['pickupLocationLevel'] = pickup_location_level
    msg_data['payload']['deliveryLocationLevel'] = delivery_location_level
    msg_data['payload']['deviceType'] = device_type

    # where do we get the ID from?
    msg_data['payload']['deviceId'] = '1234567890'

    message = ''
    try:
        communication_command = "TASK_REQUEST"
        msg_data_string = json.dumps(msg_data)
        data = communication_command + "++" + msg_data_string
        communicate_zmq(data)
    except Exception as exc:
        print('[send_task_request] %s' % str(exc))
        message = 'Command could not be sent'
    return jsonify(message=message)
