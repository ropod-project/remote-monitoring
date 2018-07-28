#!/usr/bin/env python

from __future__ import print_function
from flask import Flask

from gevent.wsgi import WSGIServer

from remote_monitoring.blueprints.black_box.black_box import black_box
from remote_monitoring.blueprints.experiments.experiments import experiments
from remote_monitoring.blueprints.ropod_status.ropod_status import ropod_status
from remote_monitoring.blueprints.task_scheduling.task_scheduling import task_scheduling

from remote_monitoring.common import zmq_context

app = Flask(__name__)
app.register_blueprint(black_box)
app.register_blueprint(experiments)
app.register_blueprint(ropod_status)
app.register_blueprint(task_scheduling)

if __name__ == '__main__':
    try:
        app.secret_key = 'area5142'
        app.config['SESSION_TYPE'] = 'filesystem'
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()
    finally:
        zmq_context.term()
