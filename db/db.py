from crypt import methods
from flask import Flask, flash, redirect, render_template, request, session, abort, flash, url_for, request, jsonify
from passlib.hash import sha256_crypt
import mysql.connector as mariadb
import json
import os
app = Flask(__name__, static_url_path="/static", template_folder="templates")
app.config["DEBUG"] = True

DB_HOST = '199.247.4.112'
DB_USER = 'sky_admin'
DB_PASSWORD = 'h^g8p{66TgW'
DB_DATABASE = 'sky_security'
DB_PORT = 3306


@app.route('/getUsers', methods = ['GET'])
def getUsr():
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    cur = conn.cursor()
    cur.execute('select * from users')
    row_headers = [x[0] for x in cur.description]
    users = cur.fetchall()
    json_data = []
    for result in users:
        json_data.append(dict(zip(row_headers, result)))

    return json.dumps(json_data)

@app.route('/getGroups', methods = ['GET'])
def getGrp():
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    cur = conn.cursor()
    cur.execute('select * from groups')
    row_headers = [x[0] for x in cur.description]
    groups = cur.fetchall()
    json_data = []
    for result in groups:
        json_data.append(dict(zip(row_headers, result)))

    return json.dumps(json_data)

@app.route('/getApps', methods = ['GET'])
def getApp():
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    cur = conn.cursor()
    cur.execute('select * from apps')
    row_headers = [x[0] for x in cur.description]
    apps = cur.fetchall()
    json_data = []
    for result in apps:
        json_data.append(dict(zip(row_headers, result)))

    return json.dumps(json_data)

@app.route('/getPerms', methods = ['GET'])
def getPerm():
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    cur = conn.cursor()
    cur.execute('select * from permissions')
    row_headers = [x[0] for x in cur.description]
    permissions = cur.fetchall()
    json_data = []
    for result in permissions:
        json_data.append(dict(zip(row_headers, result)))

    return json.dumps(json_data)


if __name__ == "__main__":
  app.secret_key = os.urandom(12)
  #context = ('cert.perm', 'key.perm')
  app.run(debug=True, host='0.0.0.0', port=5001)