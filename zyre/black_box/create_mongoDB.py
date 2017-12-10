import pymongo
from pymongo import MongoClient
import json
import collections
from bson import json_util
from pprint import pprint
import uuid
import logging
import sys
import time
from calendar import datetime


t = time.localtime()
current_time = str(t[0])+"-"+str(t[1])+"-"+str(t[2])+"T"+str(t[3])+":"+str(t[4])+":"+str(t[5])+"Z"


rec1 = {
    'timestamp': datetime.datetime.strptime('2017-12-10 3:25:40', "%Y-%m-%d %H:%M:%S"),
	'robotID':'r1',
	'pose':'5,8',
	'busy':'y',
	'battery':'51',
	'sensors':[{
	'IR':'1',
	'sonar':'0',
	'laser':'1',
	'microphone':'0'
	}
	],
	'motor values':[
	{
		'motor1':'8',
		'motor2':'9',
		'motor3':'9',
		'motor4':'8'
	}
	]
}

rec2 = {
    'timestamp': datetime.datetime.strptime('2017-12-10 4:25:40', "%Y-%m-%d %H:%M:%S"),
	'robotID':'r2',
	'pose':'0,0',
	'busy':'n',
	'battery':'85',
	'sensors':[{
	'IR':'1',
	'sonar':'1',
	'laser':'1',
	'microphone':'0'
	}
	],
	'motor values':[
	{
		'motor1':'7',
		'motor2':'5',
		'motor3':'5',
		'motor4':'8'
	}
	]
}

rec3 = {
    'timestamp': datetime.datetime.strptime('2017-12-10 5:25:40', "%Y-%m-%d %H:%M:%S"),
	'robotID':'r3',
	'pose':'5,15',
	'busy':'y',
	'battery':'45',
	'sensors':[{
	'IR':'1',
	'sonar':'1',
	'laser':'1',
	'microphone':'0'
	}
	],
	'motor values':[
	{
		'motor1':'9',
		'motor2':'8',
		'motor3':'9',
		'motor4':'7'
	}
	]
}

rec4 = {
    'timestamp': datetime.datetime.strptime('2017-12-10 5:26:40', "%Y-%m-%d %H:%M:%S"),
	'robotID':'r4',
	'pose':'10,6',
	'busy':'y',
	'battery':'88',
	'sensors':[
	{
		'IR':'1',
		'sonar':'0',
		'laser':'1',
		'microphone':'0'
		}
	],
	'motor values':[
	{
		'motor1':'5',
		'motor2':'9',
		'motor3':'9',
		'motor4':'6'
	}
	]
}

rec5 = {
    'timestamp': datetime.datetime.strptime('2017-12-11 5:25:40', "%Y-%m-%d %H:%M:%S"),
	'robotID':'r5',
	'pose':'10,9',
	'busy':'n',
	'battery':'88',
	'sensors':[
	{
	'IR':'1',
	'sonar':'0',
	'laser':'1',
	'microphone':'0'}
	],
	'motor values':[
	{
	'motor1':'9',
	'motor2':'6',
	'motor3':'8',
	'motor4':'7'
	}
	]
}


con = MongoClient()
db = con.test_db

# adding records to dataset
# members is a collection
# result = db.members.insert_one(rec1)
# result = db.members.insert_one(rec2)
# result = db.members.insert_one(rec3)
# result = db.members.insert_one(rec4)
# result = db.members.insert_one(rec5)

# print all records in the dataset
docs = db.members.find()
for d in docs:
	print(d)

print('////////////////////////////////////////////////////')
# delete records from dataset
# result = db.members.delete_many({'busy':'n'})
# result = db.members.delete_many({})

print('////////////////////////////////////////////////////')
# getting a query between two timestamp with certain feilds as answer
start_time = datetime.datetime.strptime("2017-12-10 3:55:40", "%Y-%m-%d %H:%M:%S")
end_time = datetime.datetime.strptime("2017-12-10 11:25:40", "%Y-%m-%d %H:%M:%S")

docs = db.members.find({'timestamp': {'$gte': start_time, '$lt': end_time}}, {'robotID':1, 'sensors':1, 'timestamp':1})
for doc in docs:
	print(doc)
print('////////////////////////////////////////////////////')
# getting the feilds of the first record in the dataset
# Getting the feilds of the first record of the database and convert it to a list 
feilds = [*db.members.find({})[0].keys()]
print(feilds)
print('////////////////////////////////////////////////////')
print('Finished')
