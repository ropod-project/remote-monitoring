from __future__ import print_function
import ast
import json
import uuid

from flask import Blueprint, jsonify, render_template, request, session, send_file

from remote_monitoring.common import msg_data, Config

def create_blueprint(communicator):
    black_box = Blueprint('black_box', __name__)
    zyre_communicator = communicator
    config = Config()
    query_result_file_path = '/tmp/robot_query_data.json'

    @black_box.route('/')
    def index():
        session['uid'] = uuid.uuid4()
        return render_template('index.html')

    @black_box.route('/get_robot_ids', methods=['GET'])
    def get_robot_ids():
        robots = list()
        feedback_msg = ''
        try:
            robots = config.get_robots()
        except Exception as exc:
            print('[get_robot_ids] %s' % str(exc))
            feedback_msg = 'An error occurred while retrieving the robot IDs'
        return jsonify(robots=robots, message=feedback_msg)

    @black_box.route('/get_robot_variables', methods=['GET'])
    def get_robot_variables():
        robot_id = request.args.get('robot_id', '', type=str)
        black_box_id = get_black_box_id(robot_id)

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
        # except Exception, exc:
        except Exception as exc:
            print('[get_robot_variables] %s' % str(exc))
            message = 'Variable list could not be retrieved'
        return jsonify(robot_variables=variables, message=message)

    @black_box.route('/get_robot_data', methods=['GET'])
    def get_robot_data():
        robot_id = request.args.get('robot_id', '', type=str)
        black_box_id = get_black_box_id(robot_id)

        variable_list = request.args.get('variables').split(',')

        start_query_time = request.args.get('start_timestamp')
        end_query_time = request.args.get('end_timestamp')

        query_msg = dict(msg_data)
        query_msg['header']['type'] = 'DATA_QUERY'
        query_msg['payload']['senderId'] = session['uid'].hex
        query_msg['payload']['blackBoxId'] = black_box_id
        query_msg['payload']['variables'] = variable_list
        query_msg['payload']['startTime'] = start_query_time
        query_msg['payload']['endTime'] = end_query_time
        query_result = zyre_communicator.get_black_box_data(query_msg)

        variables = list()
        data = list()
        message = ''
        try:
            variable_data = query_result['payload']['dataList']
            if variable_data is not None and variable_data[0] is not None:
                for data_dict in variable_data:
                    for key, value in data_dict.items():
                        variables.append(key)
                        variable_data_list = list()
                        for item in value:
                            variable_data_list.append(ast.literal_eval(item))
                        data.append(variable_data_list)
        # except Exception, exc:
        except Exception as exc:
            print('[get_robot_data] %s' % str(exc))
            message = 'Data could not be retrieved'
        return jsonify(variables=variables, data=data, message=message)

    @black_box.route('/get_download_query', methods=['GET'])
    def get_download_query():
        """Responds to a data download query by sending a query to the appropriate
        black box and then saving the data to a temporary file for download.
        """
        robot_id = request.args.get('robot_id', '', type=str)
        black_box_id = get_black_box_id(robot_id)

        variable_list = request.args.get('variables').split(',')

        start_query_time = request.args.get('start_timestamp')
        end_query_time = request.args.get('end_timestamp')

        query_msg = dict(msg_data)
        query_msg['header']['type'] = "DATA_QUERY"
        query_msg['payload']['senderId'] = session['uid'].hex
        query_msg['payload']['blackBoxId'] = black_box_id
        query_msg['payload']['variables'] = variable_list
        query_msg['payload']['startTime'] = start_query_time
        query_msg['payload']['endTime'] = end_query_time
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

    @black_box.route('/send_download_file', methods=['GET', 'POST'])
    def send_download_file():
        """Sends a stored data file for download.
        """
        try:
            return send_file(query_result_file_path,
                             as_attachment=True,
                             attachment_filename='robot_query_result.json')
        except Exception as exc:
            print('[send_download_file] %s' % str(exc))
            message = 'File could not be sent'
            return jsonify(message=message)

    #################
    # Helper methods
    #################
    def get_black_box_id(robot_id):
        robot_id = request.args.get('robot_id', '', type=str)
        robot_number = robot_id[robot_id.rfind('_')+1:]
        black_box_id = 'black_box_{0}'.format(robot_number)
        return black_box_id

    return black_box
