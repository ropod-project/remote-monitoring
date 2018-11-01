from __future__ import print_function
import uuid

from flask import Blueprint, jsonify, render_template, request, session

from remote_monitoring.common import msg_data, Config

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

    return task_scheduling
