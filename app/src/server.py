import os
import flask
from flask import Response
import json
import mysql.connector

from datetime import datetime
import socket

# for debugging from Visual Studio Code -- turn off flask debugger first
# import ptvsd
# ptvsd.enable_attach(address=('0.0.0.0', 3000))

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
        self.cursor.execute('CREATE TABLE daily_schedule (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), start_time DATETIME,end_time DATETIME,description VARCHAR(255)) ')
        self.cursor.executemany('INSERT INTO daily_schedule (id, name,start_time,end_time,description) VALUES (%s, %s,%s,%s,%s);', [(i, 'schedule #%d'% i,'2022/11/1','2022/11/2','ddd') for i in range (1,5)])
        self.connection.commit()


    
    def query_names(self):
        self.cursor.execute('SELECT name FROM daily_schedule')
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec



server = flask.Flask(__name__)
conn = None

@server.route('/create_schedule')
def listBlog():
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
    return flask.jsonify({"response": "Hello from Docker!"})


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
