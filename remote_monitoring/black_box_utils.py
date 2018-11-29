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
        query_msg = dict(msg_data)
        query_msg['header']['type'] = 'DATA_QUERY'
        query_msg['payload']['senderId'] = sender_id
        query_msg['payload']['blackBoxId'] = bb_id
        query_msg['payload']['variables'] = variable_list
        query_msg['payload']['startTime'] = start_query_time
        query_msg['payload']['endTime'] = end_query_time
        return query_msg

    @staticmethod
    def parse_bb_data_msg(bb_data_msg):
        '''Returns a tuple (variables, data), where variables is a list of
        variables that were queried and data a list of variable values, namely
        data[i] is a list of values corresponding to variables[i]

        Keyword arguments:
        bb_data_msg -- a black box data query response

        '''
        variables = list()
        data = list()
        if bb_data_msg:
            variable_data = bb_data_msg['payload']['dataList']
            if variable_data is not None and variable_data[0] is not None:
                for data_dict in variable_data:
                    for key, value in data_dict.items():
                        variables.append(key)
                        variable_data_list = [ast.literal_eval(item) for item in value]
                        data.append(variable_data_list)
        return (variables, data)
