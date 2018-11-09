import time
from ropod.pyre_communicator.base_class import PyreBaseCommunicator

class ZyreWebCommunicator(PyreBaseCommunicator):
    def __init__(self, node_name, groups, data_timeout=10., status_timeout=5.):
        super(ZyreWebCommunicator, self).__init__(node_name, groups, [])
        self.data_timeout = data_timeout
        self.status_timeout = status_timeout

        # a dictionary in which the keys are session IDs
        # and the values are types of requests for the particular users
        self.request_type = dict()

        # a dictionary in which the keys are session IDs
        # and the values are robots to which the requests are sent
        self.request_robots = dict()

        # a dictionary in which the keys are session IDs
        # and the values are messages for the particular users
        self.request_data = dict()

        # a dictionary in which the keys are robot IDs
        # and the values are robot status messages
        self.status_msgs = dict()

    def receive_msg_cb(self, msg_content):
        dict_msg = self.convert_zyre_msg_to_dict(msg_content)
        if dict_msg is None:
            return

        timestamp = dict_msg['header']['timestamp']
        message_type = dict_msg['header']['type']
        if message_type == 'VARIABLE_QUERY' or message_type == 'DATA_QUERY':
            for session_id in self.request_data:
                if dict_msg['payload']['receiverId'] == session_id:
                    self.request_data[session_id] = dict_msg
        elif message_type == 'HEALTH-STATUS':
            robot_id = dict_msg['payload']['robotId']
            if robot_id in self.status_msgs:
                self.status_msgs[robot_id] = dict_msg
        elif message_type == 'ROBOT-COMMAND-FEEDBACK':
            for session_id in self.request_data:
                if self.request_type[session_id] == 'ROBOT-EXPERIMENT-FEEDBACK' and \
                   self.request_robots[session_id] == dict_msg['payload']['robotId']:
                    feedback_data = dict()
                    feedback_data['timestamp'] = timestamp
                    feedback_data['feedback_type'] = message_type
                    feedback_data['robot_id'] = dict_msg['payload']['robotId']
                    feedback_data['command'] = dict_msg['payload']['command']
                    feedback_data['state'] = dict_msg['payload']['state']
                    self.request_data[session_id] = feedback_data
        elif message_type == 'ROBOT-EXPERIMENT-FEEDBACK':
            for session_id in self.request_data:
                if self.request_type[session_id] == 'ROBOT-EXPERIMENT-FEEDBACK' and \
                   self.request_robots[session_id] == dict_msg['payload']['robotId']:
                    feedback_data = dict()
                    feedback_data['timestamp'] = timestamp
                    feedback_data['feedback_type'] = message_type
                    feedback_data['robot_id'] = dict_msg['payload']['robotId']
                    feedback_data['experiment'] = dict_msg['payload']['experimentType']
                    feedback_data['result'] = dict_msg['payload']['result']
                    self.request_data[session_id] = feedback_data

    def wait_for_data(self, session_id):
        start_time = time.time()
        elapsed_time = 0.
        while not self.request_data[session_id] and elapsed_time < self.data_timeout:
            time.sleep(0.1)
            elapsed_time = time.time() - start_time

        data = None
        if self.request_data[session_id]:
            data = self.request_data[session_id]

        self.request_data.pop(session_id)
        if session_id in self.request_robots:
            self.request_robots.pop(session_id)
        if session_id in self.request_type:
            self.request_type.pop(session_id)
        return data

    ############
    # Black box
    ###########
    def get_black_box_data(self, query_msg):
        session_id = query_msg['payload']['senderId']
        self.request_data[session_id] = None
        self.request_robots[session_id] = query_msg['payload']['blackBoxId']
        self.shout(query_msg)
        data = self.wait_for_data(session_id)
        return data

    #####################
    # Component monitors
    #####################
    def get_status(self, robot_id):
        if self.status_msgs[robot_id] and self.status_msgs[robot_id]['header']['timestamp']:
            time_since_last_msg = time.time() - self.status_msgs[robot_id]['header']['timestamp']
            if time_since_last_msg > self.status_timeout:
                self.status_msgs[robot_id]['payload']['monitors'] = None
        return self.status_msgs[robot_id]

    #####################
    # Remote experiments
    #####################
    def get_experiment_feedback(self, session_id, robot_id):
        self.request_data[session_id] = None
        self.request_robots[session_id] = robot_id
        self.request_type[session_id] = 'ROBOT-EXPERIMENT-FEEDBACK'
        experiment_feedback = self.wait_for_data(session_id)
        return experiment_feedback
