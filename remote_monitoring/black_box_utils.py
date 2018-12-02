from copy import deepcopy
import time
import ast

from remote_monitoring.common import msg_data

class BBUtils(object):
    '''A collection of methods for simplifying the interaction with a robot black box.

    Author -- Alex Mitrevski
    Contact -- aleksandar.mitrevski@h-brs.de

    '''
    @staticmethod
    def get_bb_id(robot_id):
        '''Extracts the ID of the robot and creates the ID of the black box
        corresponding to that robot. The robot ID is assumed to be in the form
        robot_<xxx>, where <xxx> is the actual ID and the resulting
        black box ID will have the form black_box_<xxx>

        Keyword arguments:
        robot_id -- ID of a robot

        '''
        robot_number = robot_id[robot_id.rfind('_')+1:]
        black_box_id = 'black_box_{0}'.format(robot_number)
        return black_box_id

    @staticmethod
    def get_robot_id(black_box_id):
        '''Extracts the ID of the black box and creates the ID of the robot
        corresponding to that black box. The black box ID is assumed to be in the form
        black_box_<xxx>, where <xxx> is the actual ID and the resulting
        robot ID will have the form robot_<xxx>

        Keyword arguments:
        black_box_id -- ID of a black box

        '''
        black_box_number = black_box_id[black_box_id.rfind('_')+1:]
        robot_id = 'robot_{0}'.format(black_box_number)
        return robot_id

    @staticmethod
    def expand_var_names(variables, index_count):
        '''Generates a new list of variable names from "variables" such that
        the * character in each entry of "variables" is replaced by a one-based index
        (the number of indices is determined by "index_count").

        Example:
        If "variables" is the list ["var1/*", "var2/*"], and "index_count" is 3, the
        resulting list will be ["var1/1", "var1/2", "var1/3", "var2/1", "var2/2", "var2/3"].

        Keyword arguments:
        variables -- a list of variable names including a * as an index replacement
        index_count -- number of times each variable should be expanded

        '''
        expanded_vars = [var.replace('*', str(i+1))
                         for var in variables
                         for i in range(index_count)]
        return expanded_vars

    @staticmethod
    def get_bb_query_msg(sender_id, bb_id, variable_list, start_query_time, end_query_time):
        '''Returns a black box query message as defined in
        https://git.ropod.org/ropod/communication/ropod-models/blob/develop/schemas/black-box/ropod-black-box-data-query-schema.json

        Keyword arguments:
        sender_id -- ID of the user that queries the data (typically a session ID)
        bb_id -- ID of the black box that should be queried (of the form black_box_<xxx>)
        variable_list -- a list of variables whose values are queried
        start_query_time -- UNIX timestamp denoting the start data query time
        end_query_time -- UNIX timestamp denoting the end data query time

        '''
        query_msg = deepcopy(msg_data)
        query_msg['header']['type'] = 'DATA-QUERY'
        query_msg['header']['timestamp'] = time.time()
        query_msg['payload']['senderId'] = sender_id
        query_msg['payload']['blackBoxId'] = bb_id
        query_msg['payload']['variables'] = variable_list
        query_msg['payload']['startTime'] = start_query_time
        query_msg['payload']['endTime'] = end_query_time
        return query_msg

    @staticmethod
    def get_bb_latest_data_query_msg(sender_id, bb_id, variable_list):
        '''Returns a black box query message as defined in
        https://git.ropod.org/ropod/communication/ropod-models/blob/develop/schemas/black-box/ropod-black-box-latest-data-query-schema.json

        Keyword arguments:
        sender_id -- ID of the user that queries the data (typically a session ID)
        bb_id -- ID of the black box that should be queried (of the form black_box_<xxx>)
        variable_list -- a list of variables whose values are queried

        '''
        query_msg = deepcopy(msg_data)
        query_msg['header']['type'] = 'LATEST-DATA-QUERY'
        query_msg['header']['timestamp'] = time.time()
        query_msg['payload']['senderId'] = sender_id
        query_msg['payload']['blackBoxId'] = bb_id
        query_msg['payload']['variables'] = variable_list
        return query_msg

    @staticmethod
    def parse_bb_variable_msg(bb_variable_msg):
        '''Returns a nested dictionary that reconstructs the structure of the
        data represented by the variables in bb_variable_msg["payload"]["variableList"]

        Example:
        If bb_variable_msg["payload"]["variableList"] is the nested dictionary
        {
            'ros': ['ros_cmd_vel/linear/z', 'ros_cmd_vel/linear/x', 'ros_cmd_vel/angular/x',
                    'ros_cmd_vel/angular/z', 'ros_cmd_vel/angular/y', 'ros_cmd_vel/linear/y',
                    'ros_pose/x', 'ros_pose_y', 'ros_pose_z'],
            'zyre': ['zyre_pose/x', 'zyre_pose_y', 'zyre_pose_z']
        }
        the resulting nested dictionary will be
        {
            'ros_cmd_vel':
            {
                'linear':
                {
                    'x': {}
                    'y': {},
                    'z': {}
                },
                'angular':
                {
                    'x': {}
                    'y': {},
                    'z': {}
                }
            },
            'ros_pose':
            {
                'x': {},
                'y': {},
                'z': {}
            },
            'zyre_pose':
            {
                'x': {},
                'y': {},
                'z': {}
            }
        }

        Keyword arguments:
        bb_variable_msg -- a black box variable query response

        '''
        variables = dict()
        if bb_variable_msg:
            for variable_names in bb_variable_msg['payload']['variableList'].values():
                if variable_names:
                    for full_variable_name in variable_names:
                        slash_indices = [0]
                        current_variable_dict = variables
                        for i, char in enumerate(full_variable_name):
                            if char == '/':
                                slash_indices.append(i+1)
                                name_component = full_variable_name[slash_indices[-2]:
                                                                    slash_indices[-1]-1]
                                if name_component not in current_variable_dict:
                                    current_variable_dict[name_component] = dict()
                                current_variable_dict = current_variable_dict[name_component]
                        name_component = full_variable_name[slash_indices[-1]:]
                        current_variable_dict[name_component] = dict()
        return variables

    @staticmethod
    def parse_bb_data_msg(bb_data_msg):
        '''Returns a tuple (variables, data), where variables is a list of
        variables that were queried and data a list of variable values, namely
        data[i] is a list of [timestamp, value] lists corresponding to variables[i]

        Keyword arguments:
        bb_data_msg -- a black box data query response

        '''
        variables = list()
        data = list()
        if bb_data_msg:
            for var_name, var_data in bb_data_msg['payload']['dataList'].items():
                variables.append(var_name)
                variable_data_list = [ast.literal_eval(item) for item in var_data]
                data.append(variable_data_list)
        return (variables, data)

    @staticmethod
    def parse_bb_latest_data_msg(bb_data_msg):
        '''Returns a tuple (variables, data), where variables is a list of
        variables that were queried and data a list of the latest variable values,
        namely data[i] is a list [timestamp, value] corresponding to
        the latest value of variables[i] along with its timestamp

        Keyword arguments:
        bb_data_msg -- a black box latest data query response

        '''
        variables = list()
        data = list()
        if bb_data_msg:
            for var_name, var_data in bb_data_msg['payload']['dataList'].items():
                variables.append(var_name)
                if var_data:
                    data.append(ast.literal_eval(var_data))
                else:
                    data.append(None)
        return (variables, data)
