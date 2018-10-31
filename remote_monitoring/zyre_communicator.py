import time
from pyre_communicator.base_class import PyreBaseCommunicator

class ZyreWebCommunicator(PyreBaseCommunicator):
    def __init__(self, node_name, groups, data_timeout=10.):
        super(ZyreWebCommunicator, self).__init__(node_name, groups, [])
        self.data_timeout = data_timeout

        # a dictionary in which the keys are session IDs
        # and the values are types of requests for the particular users
        self.request_type = dict()

        # a dictionary in which the keys are session IDs
        # and the values are messages for the particular users
        self.request_data = dict()

    def receive_msg_cb(self, msg_content):
        dict_msg = self.convert_zyre_msg_to_dict(msg_content)
        if dict_msg is None:
            return

        message_type = dict_msg['header']['type']
        if message_type == 'ROBOT-COMMAND-FEEDBACK':
            for session_id in self.request_type:
                if self.request_type[session_id] == 'ROBOT-EXPERIMENT-FEEDBACK':
                    feedback_data = dict()
                    feedback_data['timestamp'] = dict_msg['header']['timestamp']
                    feedback_data['feedback_type'] = 'ROBOT-COMMAND-FEEDBACK'
                    feedback_data['robot_id'] = dict_msg['payload']['robotId']
                    feedback_data['command'] = dict_msg['payload']['command']
                    feedback_data['state'] = dict_msg['payload']['state']
                    self.request_data[session_id] = feedback_data
        elif message_type == 'ROBOT-EXPERIMENT-FEEDBACK':
            for session_id in self.request_type:
                if self.request_type[session_id] == 'ROBOT-EXPERIMENT-FEEDBACK':
                    feedback_data = dict()
                    feedback_data['timestamp'] = dict_msg['header']['timestamp']
                    feedback_data['feedback_type'] = 'ROBOT-EXPERIMENT-FEEDBACK'
                    feedback_data['robot_id'] = dict_msg['payload']['robotId']
                    feedback_data['experiment'] = dict_msg['payload']['experimentType']
                    feedback_data['result'] = dict_msg['payload']['result']
                    self.request_data[session_id] = feedback_data

    def get_experiment_feedback(self, session_id):
        self.request_data[session_id] = None
        self.request_type[session_id] = 'ROBOT-EXPERIMENT-FEEDBACK'
        start_time = time.time()
        elapsed_time = 0.
        while not self.request_data[session_id] and elapsed_time < self.data_timeout:
            time.sleep(0.1)
            elapsed_time = time.time() - start_time

        experiment_feedback = None
        if self.request_data[session_id]:
            experiment_feedback = self.request_data[session_id]
        self.request_data.pop(session_id)
        self.request_type.pop(session_id)
        return experiment_feedback
