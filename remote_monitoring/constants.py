class LocalDbConstants(object):
    DATABASE = 'ropods'
    COLLECTION = 'ropod_data'

class DbConstants(object):
    DATABASE = 'aiciss_logs'
    COLLECTION = 'robot_state'

class VariableConstants(object):
    POSE = 'pose'
    BATTERY_STATUS = 'battery_status'
    EXTERNAL_SOURCE_STATUS = 'external_source_status'
    WHEEL_FAULT_STATUS = 'wheel_fault_status'
    WHEEL_CURRENTS = 'wheel_currents'
    WHEEL_ANGLES = 'wheel_angles'
    WHEEL_VELOCITIES = 'wheel_velocities'
    WHEEL_TORQUES = 'wheel_torques'
    EXPECTED_WHEEL_VELOCITIES = 'expected_wheel_velocities'
    ROBOT_VELOCITY = 'robot_velocity'
    ROBOT_VELOCITY_CMD = 'robot_velocity_cmd'

    @staticmethod
    def get_logged_variable_list():
        keys = ['pose', 'battery_status', 'external_source_status', 'wheel_fault_status', 'wheel_currents', 'wheel_angles', 'wheel_velocities', 'wheel_torques', 'expected_wheel_velocities', 'robot_velocity', 'robot_velocity_cmd']
        labels = ['Pose', 'Battery status', 'External source status', 'Wheel fault status', 'Wheel currents', 'Wheel angles', 'Wheel velocities', 'Wheel torques', 'Expected wheel velocities', 'Robot velocity', 'Robot velocity command']
        return keys, labels
