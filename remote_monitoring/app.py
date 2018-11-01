#!/usr/bin/env python

from __future__ import print_function
from flask import Flask

import remote_monitoring.blueprints.black_box.black_box as black_box
import remote_monitoring.blueprints.experiments.experiments as experiments
from remote_monitoring.blueprints.ropod_status.ropod_status import ropod_status
import remote_monitoring.blueprints.task_scheduling.task_scheduling as task_scheduling

from remote_monitoring.common import zmq_context
from remote_monitoring.common import socketio

from remote_monitoring.zyre_communicator import ZyreWebCommunicator

zyre_communicator = ZyreWebCommunicator('remote_monitoring',
                                        ['ROPOD', 'MONITORING'], 10.)

app = Flask(__name__)
app.register_blueprint(black_box.create_blueprint(zyre_communicator))
app.register_blueprint(experiments.create_blueprint(zyre_communicator))
app.register_blueprint(ropod_status)
app.register_blueprint(task_scheduling.create_blueprint(zyre_communicator))

socketio.init_app(app)

if __name__ == '__main__':
    try:
        app.secret_key = 'area5142'
        app.config['SESSION_TYPE'] = 'filesystem'
        socketio.run(app, host='0.0.0.0')
    finally:
        zyre_communicator.shutdown()
        zmq_context.term()
