from itertools import count
from math import perm
from flask import Flask, flash, redirect, render_template, request, session, abort, flash, url_for, request, jsonify
from flask_restful import Resource, Api
from passlib.hash import sha256_crypt
import mysql.connector as mariadb
import plotly
import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.offline import init_notebook_mode
import json
import plotly.express as px
import os

app = Flask(__name__, static_url_path="/static", template_folder="templates")
api = Api(app)
app.config["DEBUG"] = True


DB_HOST = '199.247.4.112'
DB_USER = 'sky_admin'
DB_PASSWORD = 'h^g8p{66TgW'
DB_DATABASE = 'sky_security'
DB_PORT = 3306


@app.route("/admin_dashboard1", methods = ['POST', 'GET'])
def do_dasboard_apps():
    apps = "select count(*), name from apps group by name;"
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        cur.execute(apps)
        apps = cur.fetchall()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')
    
    applications = []
    valuesApps = []

    for list in apps:
        for el in list:
            if (isinstance(el, str)):
                applications.append(el)
            else:
                valuesApps.append(el)
            

    fig = go.Figure(data=[go.Pie(labels=applications, values = valuesApps)])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
   
    return graphJSON

@app.route("/admin_dashboard2", methods = ['POST', 'GET'])
def do_dashboard_perms():
    users_perms = ("select perm.name, count(*) from permissions as perm "
                "inner join groups_perm_relation gpr on gpr.perm_id = perm.id "
                "inner join user_groups_relation as ugr "
                "on ugr.group_id = gpr.group_id group by perm.name;")

    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        cur.execute(users_perms)
        users_perms = cur.fetchall()
        
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')


    permission = []
    count_perms = []

    for list in users_perms:
        for el in list:
            if (isinstance(el, str)):
                permission.append(el)
            else:
                count_perms.append(el)

    
    fig = px.line(x=permission, y=count_perms, 
            labels=dict(x="Permission", y="Amount", color="Time Period"))
    fig.add_bar(x=permission, y=count_perms, name="Counter")
    fig.update_layout(title_text="Multi-category axis")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON




@app.route("/admin_dashboard3", methods = ['POST', 'GET'])
def do_dashboard():

    group_names = ("select g.name, count(*) from groups as g inner join "
                    "user_groups_relation as ugr on ugr.group_id = g.id inner "
                    "join users as u on u.id = ugr.user_id group by g.name;")
    
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        cur.execute(group_names)
        group_names = cur.fetchall()
        print(group_names)
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

    gr_name = []
    values = []

    for list in group_names:
        for el in list:
            if (isinstance(el, str)):
                gr_name.append(el)
            else:
                values.append(el)
   
    fig = go.Figure(data=[go.Pie(labels=gr_name,
                        values=values)])
    

    #CONVERTING A GRAPH TO A JSON GRAPH
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return  graphJSON #fig2.show()


@app.route('/', methods=['GET'])
def serve():
    return "yoyo", 200

if __name__ == "__main__":
  app.secret_key = os.urandom(12)
  #context = ('cert.perm', 'key.perm')
  app.run(debug=True, host='0.0.0.0', port=5003)