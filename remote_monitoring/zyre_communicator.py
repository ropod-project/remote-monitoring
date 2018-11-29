from copy import deepcopy
import time
from ropod.pyre_communicator.base_class import PyreBaseCommunicator
from remote_monitoring.common import Config, robot_status_msg

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

        # a dictionary in which the keys are robot IDs
        # and the values are experiment feedback messages
        self.experiment_feedback_msgs = dict()

        # a dictionary in which the keys are robot IDs
        # and the values are the corresponding robot poses
        self.robot_pose_msgs = dict()

        config = Config()
        robots = config.get_robots()
        for robot in robots:
            status_msg = deepcopy(robot_status_msg)
            status_msg['payload']['robotId'] = robot
            self.status_msgs[robot] = status_msg
            self.experiment_feedback_msgs[robot] = None

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
            robot_id = dict_msg['payload']['robotId']
            if robot_id in self.experiment_feedback_msgs:
                feedback_data = dict()
                feedback_data['timestamp'] = timestamp
                feedback_data['feedback_type'] = message_type
                feedback_data['robot_id'] = dict_msg['payload']['robotId']
                feedback_data['command'] = dict_msg['payload']['command']
                feedback_data['state'] = dict_msg['payload']['state']
                self.experiment_feedback_msgs[robot_id] = feedback_data
        elif message_type == 'ROBOT-EXPERIMENT-FEEDBACK':
            robot_id = dict_msg['payload']['robotId']
            if robot_id in self.experiment_feedback_msgs:
                feedback_data = dict()
                feedback_data['timestamp'] = timestamp
                feedback_data['feedback_type'] = message_type
                feedback_data['robot_id'] = dict_msg['payload']['robotId']
                feedback_data['experiment'] = dict_msg['payload']['experimentType']
                feedback_data['result'] = dict_msg['payload']['result']
                self.experiment_feedback_msgs[robot_id] = feedback_data
        elif message_type == 'RobotPose2D':
            robot_id = dict_msg['payload']['robotId']
            if robot_id in self.experiment_feedback_msgs:
                self.robot_pose_msgs[robot_id] = dict_msg

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
    # Robot pose
    #####################
    def get_pose(self, robot_id):
        if robot_id in self.robot_pose_msgs.keys() and self.robot_pose_msgs[robot_id]['header']['timestamp']:
            return self.robot_pose_msgs[robot_id]
        else:
            return None

    #####################
    # Remote experiments
    #####################
    def get_experiment_feedback(self, robot_id):
        # if there are no experiment feedback messages, we wait until we
        # get one or until the status timeout is reached
        start_time = time.time()
        elapsed_time = 0.
        while not self.experiment_feedback_msgs[robot_id] and elapsed_time < self.status_timeout:
            time.sleep(0.1)
            elapsed_time = time.time() - start_time

        # if we do have a saved feedback message, but it was received
        # a long time ago, we clear the message
        if self.experiment_feedback_msgs[robot_id]:
            last_msg_time_diff = time.time() - self.experiment_feedback_msgs[robot_id]['timestamp']
            if last_msg_time_diff > self.status_timeout:
                self.experiment_feedback_msgs[robot_id] = None

        feedback_msg = self.experiment_feedback_msgs[robot_id]
        if feedback_msg and feedback_msg['feedback_type'] == 'ROBOT-EXPERIMENT-FEEDBACK':
            self.experiment_feedback_msgs[robot_id] = None
        return feedback_msg
