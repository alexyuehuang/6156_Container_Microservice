import os
import flask
from flask import Response
from flask import request
import json
import mysql.connector

from datetime import datetime
import socket

# reference from ed github link
USR_SHOPPING_PROPS = {
    'microservice': 'User shopping list microservice',
    'api': 'http://127.0.0.1/shopping_list', #TO DO
    'fields': ('user', 'list')
}
USR_TRAVEL_PROPS = {
    'microservice': 'User travel plan microservice',
    'api': 'http://127.0.0.1/travel_plan',
    'fields': ('user', 'destination', 'startdate', 'enddate', 'detailed_plan')
}
USR_SCHEDULE_PROPS = {
    'microservice': 'User schedule microservice',
    'api': 'http://127.0.0.1/list_schedule',
    'fields': ('name', 'start_time', 'end_time', 'description')
}
PROPS = (USR_TRAVEL_PROPS, USR_SHOPPING_PROPS, USR_SCHEDULE_PROPS)

class DBManager:
    def __init__(self, database='example', host="db", user="root", password_file=None):
        pf = open(password_file, 'r')
        self.connection = mysql.connector.connect(
            user=user, 
            password=pf.read(),
            host=host,
            database=database,
            auth_plugin='mysql_native_password'
        )
        pf.close()
        self.cursor = self.connection.cursor()
    
    def create_db(self):
        self.cursor.execute('DROP TABLE IF EXISTS daily_schedule')
        # self.cursor.execute('CREATE TABLE daily_schedule (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), start_time DATETIME,end_time DATETIME,description VARCHAR(255)) ')
        # self.cursor.executemany('INSERT INTO daily_schedule (id, name,start_time,end_time,description) VALUES (%s, %s,%s,%s,%s);', [(i, 'schedule #%d'% i,'2022/11/1','2022/11/2','ddd') for i in range (1,5)])
        self.cursor.execute(
            'CREATE TABLE daily_schedule (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), start_time VARCHAR(255),end_time VARCHAR(255),description VARCHAR(255)) ')

        self.cursor.executemany(
            'INSERT INTO daily_schedule (id, name,start_time,end_time,description) VALUES (%s, %s,%s,%s,%s);',
            [(i, 'schedule #%d' % i, '2022/11/1', '2022/11/2', 'ddd') for i in range(1, 5)])

        self.connection.commit()

    def query_names(self):
        self.cursor.execute('SELECT name FROM daily_schedule')
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec

    def query_all(self):
        self.cursor.execute('SELECT * FROM daily_schedule')
        rec = []
        for c in self.cursor:
            # print(c)
            # rec.append(c[0])
            rec.append(c)
        return rec

    def create_entry(self, name, start, end, description):
        # self.cursor.execute(
        # 'INSERT INTO daily_schedule (id, name,start_time,end_time,description) VALUES (%s, %s,%s,%s,%s);',
        # (0, name, start, end, description))
        self.cursor.execute(
            'INSERT INTO daily_schedule ( name,start_time,end_time,description) VALUES (%s,%s,%s,%s);',
            (name, start, end, description))
        self.connection.commit()



server = flask.Flask(__name__)
conn = None

# /add_schedule/aaa/2000-01-01/2000-01-02/abc
@server.route('/add_schedule/<name>/<start_time>/<end_time>/<description>')
def add_schedule(name, start_time, end_time, description):
    global conn
    conn.create_entry(name, start_time, end_time, description)
    return flask.jsonify({"response": "success"})



@server.route('/list_schedule')
def list_schedule():
    global conn
    # rec = conn.query_names()
    rec = conn.query_all()
    result = []
    for c in rec:
        result.append(c)
    return flask.jsonify({"response": result})

@server.route('/create_schedule')
def create_schedule():
    global conn
    if not conn:
        conn = DBManager(password_file='/run/secrets/db-password')
        conn.create_db()
    rec = conn.query_names()

    result = []
    for c in rec:
        result.append(c)

    return flask.jsonify({"response": result})

@server.route('/')
def hello():
    return flask.jsonify({"Welcome to our website"})


@server.route('/health')
def health():

    result = {
        "service-name": "dockercon2020-demo: app",
        "status": "healthy",
        "at-time": str(datetime.now()),
        "address": str(socket.gethostbyname(socket.gethostname()))
    }
    rsp = Response(json.dumps(result, indent=2, default=str), 200, content_type="application/json")
    return rsp


if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0', port=5000)
