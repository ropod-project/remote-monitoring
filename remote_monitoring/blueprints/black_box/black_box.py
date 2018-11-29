from __future__ import print_function
import json
import uuid

from flask import Blueprint, jsonify, render_template, request, session, send_file

from remote_monitoring.common import msg_data, Config
from remote_monitoring.black_box_utils import BBUtils

def create_blueprint(communicator):
    black_box = Blueprint('black_box', __name__)
    zyre_communicator = communicator
    config = Config()
    query_result_file_path = '/tmp/robot_query_data.json'

    @black_box.route('/black_box')
    def index():
        session['uid'] = uuid.uuid4()
        return render_template('black_box.html')

    @black_box.route('/black_box/get_robot_ids', methods=['GET'])
    def get_robot_ids():
        robots = list()
        feedback_msg = ''
        try:
            robots = config.get_robots()
        except Exception as exc:
            print('[get_robot_ids] %s' % str(exc))
            feedback_msg = 'An error occurred while retrieving the robot IDs'
        return jsonify(robots=robots, message=feedback_msg)

    @black_box.route('/black_box/get_robot_variables', methods=['GET'])
    def get_robot_variables():
        robot_id = request.args.get('robot_id', '', type=str)
        black_box_id = BBUtils.get_bb_id(robot_id)

        query_msg = dict(msg_data)
        query_msg['header']['type'] = 'VARIABLE_QUERY'
        query_msg['payload']['senderId'] = session['uid'].hex
        query_msg['payload']['blackBoxId'] = black_box_id
        query_result = zyre_communicator.get_black_box_data(query_msg)

        variables = dict()
        message = ''
        try:
            for interface in query_result['payload']['variableList']:
                values = list(interface.values())
                if values is not None and values[0] is not None:
                    for full_variable_name in values[0]:
                        underscore_indices = [0]
                        current_variable_dict = variables
                        for i, char in enumerate(full_variable_name):
                            if char == '/':
                                underscore_indices.append(i+1)
                                name_component = full_variable_name[underscore_indices[-2]:underscore_indices[-1]-1]
                                if name_component not in current_variable_dict:
                                    current_variable_dict[name_component] = dict()
                                current_variable_dict = current_variable_dict[name_component]
                        name_component = full_variable_name[underscore_indices[-1]:]
                        current_variable_dict[name_component] = dict()
        except Exception as exc:
            print('[get_robot_variables] %s' % str(exc))
            message = 'Variable list could not be retrieved'
        return jsonify(robot_variables=variables, message=message)

    @black_box.route('/black_box/get_robot_data', methods=['GET'])
    def get_robot_data():
        robot_id = request.args.get('robot_id', '', type=str)
        black_box_id = BBUtils.get_bb_id(robot_id)
        variable_list = request.args.get('variables').split(',')
        start_query_time = request.args.get('start_timestamp')
        end_query_time = request.args.get('end_timestamp')

        query_msg = BBUtils.get_bb_query_msg(session['uid'].hex,
                                             black_box_id,
                                             variable_list,
                                             start_query_time,
                                             end_query_time)
        query_result = zyre_communicator.get_black_box_data(query_msg)

        variables = list()
        data = list()
        message = ''
        try:
            variables, data = BBUtils.parse_bb_data_msg(query_result)
        except Exception as exc:
            print('[get_robot_data] %s' % str(exc))
            message = 'Data could not be retrieved'
        return jsonify(variables=variables, data=data, message=message)

    @black_box.route('/black_box/get_download_query', methods=['GET'])
    def get_download_query():
        '''Responds to a data download query by sending a query to the appropriate
        black box and then saving the data to a temporary file for download.
        '''
        robot_id = request.args.get('robot_id', '', type=str)
        black_box_id = BBUtils.get_bb_id(robot_id)
        variable_list = request.args.get('variables').split(',')
        start_query_time = request.args.get('start_timestamp')
        end_query_time = request.args.get('end_timestamp')

        query_msg = BBUtils.get_bb_query_msg(session['uid'].hex,
                                             black_box_id,
                                             variable_list,
                                             start_query_time,
                                             end_query_time)
        query_result = zyre_communicator.get_black_box_data(query_msg)

        message = ''
        try:
            with open(query_result_file_path, 'w') as download_file:
                json.dump(query_result, download_file)
            return jsonify(success=True)
        except Exception as exc:
            print('[get_download_query_robot_data] %s' % str(exc))
            message = 'Data could not be retrieved'
            return jsonify(message=message)

    @black_box.route('/black_box/send_download_file', methods=['GET', 'POST'])
    def send_download_file():
        '''Sends a stored data file for download.
        '''
        try:
            return send_file(query_result_file_path,
                             as_attachment=True,
                             attachment_filename='robot_query_result.json')
        except Exception as exc:
            print('[send_download_file] %s' % str(exc))
            message = 'File could not be sent'
            return jsonify(message=message)

    return black_box
