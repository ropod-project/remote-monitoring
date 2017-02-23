from flask import Flask, jsonify, render_template, request, redirect, url_for
from datetime import datetime

from constants import DbConstants, VariableConstants
from db import DbConnection, DbQueries

app = Flask(__name__)
db_connection = DbConnection(DbConstants.HOST_ADDRESS, DbConstants.DATABASE, DbConstants.COLLECTION)

@app.route('/')
def index():
    variable_keys, variable_labels = VariableConstants.get_logged_variable_list()
    return render_template('index.html', variable_keys=variable_keys, variable_labels=variable_labels)

@app.route('/get_data', methods=['GET', 'POST'])
def get_data():
    variable = request.args.get('variable', '', type=str)
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)

    start_date_components = start_date.split('/')
    end_date_components = end_date.split('/')

    start_time = datetime(int(start_date_components[2]), int(start_date_components[0]), int(start_date_components[1]))
    end_time = datetime(int(end_date_components[2]), int(end_date_components[0]), int(end_date_components[1]))

    start_timestamp = (start_time - datetime(1970, 1, 1)).total_seconds() * 1000
    end_timestamp = (end_time - datetime(1970, 1, 1)).total_seconds() * 1000

    data, data_labels = DbQueries.get_data(db_connection, variable, start_timestamp, end_timestamp)
    return jsonify(data=data, data_labels=data_labels)
    
if __name__ == '__main__':
    app.run()
