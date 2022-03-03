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




@app.route("/admin_dashboard", methods = ['POST', 'GET'])
def do_dashboard():

    group_names = ("select g.name, count(*) from groups as g inner join "
                    "user_groups_relation as ugr on ugr.group_id = g.id inner "
                    "join users as u on u.id = ugr.user_id group by g.name;")
    apps = "select count(*), name from apps group by name;"
    query = ("SELECT gpr.perm_id, p.name, g.name, a.name FROM "
             "groups_perm_relation AS gpr INNER JOIN groups AS g "
             "ON g.id = gpr.group_id INNER JOIN permissions AS p "
             "ON gpr.perm_id = p.id INNER JOIN apps AS a ON p.app_id = a.id "
             "WHERE perm_id IN (  SELECT id FROM permissions WHERE app_id = 3)"
             " ORDER BY p.name;")
    users_perms = ("select perm.name, count(*) from permissions as perm "
                "inner join groups_perm_relation gpr on gpr.perm_id = perm.id "
                "inner join user_groups_relation as ugr "
                "on ugr.group_id = gpr.group_id group by perm.name;")
    
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        cur.execute(group_names)
        group_names = cur.fetchall()
        cur.execute(apps)
        apps = cur.fetchall()
        cur.execute(users_perms)
        users_perms = cur.fetchall()
        print(users_perms)
        cur.execute(query)
        perms_app = cur.fetchall()
        print(perms_app)
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')


    permission = [users_perms[0][0], users_perms[1][0], users_perms[2][0], 
                  users_perms[3][0], users_perms[4][0], users_perms[5][0], 
                  users_perms[6][0]]
    count_perms = [users_perms[0][1], users_perms[1][1], users_perms[2][1], 
                   users_perms[3][1], users_perms[4][1], users_perms[5][1], 
                   users_perms[6][1]]
    fig3 = px.line(x=permission, y=count_perms, 
            labels=dict(x="Permission", y="Amount", color="Time Period"))
    fig3.add_bar(x=permission, y=count_perms, name="Counter")
    fig3.update_layout(title_text="Multi-category axis")


    graphJSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
   
    perms = [group_names[0][0],group_names[1][0],
            group_names[2][0],group_names[3][0],
            group_names[4][0],group_names[5][0],
            group_names[6][0]]

    values = [group_names[0][1],group_names[1][1],
            group_names[2][1],group_names[3][1],
            group_names[4][1],group_names[5][1],
            group_names[6][1]]
   
    fig = go.Figure(data=[go.Pie(labels=perms,
                        values=values)])
    

    #CONVERTING A GRAPH TO A JSON GRAPH
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

   
    applications = [apps[0][1], apps[1][1]]

    valuesApps = [apps[0][0], apps[1][0]]

    fig2 = go.Figure(data=[go.Pie(labels=applications, values = valuesApps)])

    graphJSON3 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)


    #return render_template('admin_files/admin_dashboard.html', 
       # graphJSON = graphJSON, graphJSON2=graphJSON2, graphJSON3 = graphJSON3)
    return graphJSON


@app.route('/', methods=['GET'])
def serve():
    return "Hello world", 200

if __name__ == "__main__":
  app.secret_key = os.urandom(12)
  #context = ('cert.perm', 'key.perm')
  app.run(debug=True, host='0.0.0.0', port=5003)