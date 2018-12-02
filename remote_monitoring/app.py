#!/usr/bin/env python

from __future__ import print_function
from flask import Flask

import remote_monitoring.blueprints.black_box.black_box as black_box
import remote_monitoring.blueprints.experiments.experiments as experiments
import remote_monitoring.blueprints.ropod_status.robot_status as robot_status
import remote_monitoring.blueprints.real_time_monitoring.real_time_monitoring as real_time_monitoring
import remote_monitoring.blueprints.task_scheduling.task_scheduling as task_scheduling

from remote_monitoring.common import socketio
from remote_monitoring.zyre_communicator import ZyreWebCommunicator

zyre_communicator = ZyreWebCommunicator('remote_monitoring', ['ROPOD', 'MONITOR'],
                                        data_timeout=10., status_timeout=5.)

app = Flask(__name__)
app.register_blueprint(black_box.create_blueprint(zyre_communicator))
app.register_blueprint(experiments.create_blueprint(zyre_communicator))
app.register_blueprint(robot_status.create_blueprint(zyre_communicator))
app.register_blueprint(task_scheduling.create_blueprint(zyre_communicator))
app.register_blueprint(real_time_monitoring.create_blueprint(zyre_communicator))

socketio.init_app(app)

if __name__ == '__main__':
    try:
        app.secret_key = 'area5142'
        app.config['SESSION_TYPE'] = 'filesystem'
        socketio.run(app, host='0.0.0.0')
    finally:
        zyre_communicator.shutdown()
