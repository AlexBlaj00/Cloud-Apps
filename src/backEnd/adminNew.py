from flask_restful import Resource, Api
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

#==============================================================================#
@app.route('/admin_home')
def admin_home_run():
   # if the user is not logged in, redirect him/her to the login page
    #is_logged_in()

    # list of queries
    queries = []

    # create query to get the pemissions of the user based on the groups that
    # the user is a part of

    #query on app to see waht permission you have for every app you have access
    queries.append(
        "SELECT * FROM permissions p "
        "INNER JOIN groups_perm_relation gp ON gp.perm_id = p.id "
        "WHERE gp.group_id IN ( "
        "SELECT g.id FROM groups g "
        "INNER JOIN user_groups_relation ug ON ug.group_id = g.id "
        "WHERE ug.user_id = 1"  + ");")

    # database connection 
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered=True)       

        # get all the permissions for this user based on the groups that 
        # the user is a part of
        cur.execute(queries[0])
        permissions = cur.fetchall()    
        
        # store the distinct app ids
        app_ids = []

        # create the list of unique apps that the user has access to
        for p in permissions:
            if p[3] not in app_ids:
                app_ids.append(p[3])
        
        # select the app names and ids based on the list created
        queries.append("SELECT * FROM apps WHERE id IN" 
                       + form_delete_id_string(app_ids, True))
        
        # fetch the apps
        cur.execute(queries[1])
        apps = cur.fetchall()

        # store the id and name in a {id : name} format
        app_id_name = {}
        for app in apps:
            app_id_name[app[0]] = app[1]

        app_perms_list = {}

        # initialize the dictionary with the app name as a key and an empty list that 
        # will be filled later with the permissions
        for name in app_id_name.values():
            app_perms_list[ name ] = []

        # for each permission get the app_id and search it in the app_id_name
        # to get the name of the app and append the permission to the list
        # that has the name as a key
        for p in permissions:
            if p[3] in app_id_name.keys():
                is_in_list = False
                for perm in app_perms_list[ app_id_name[p[3]] ]:
                    if p[1] == perm[1]:
                        is_in_list = True
                        break
                if not is_in_list:
                    app_perms_list[ app_id_name[p[3]] ].append(p)


        # close the connection
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')


    # return the page with all the data stored in the app_perms_list variable
    #return render_template('admin_files/admin_home.html', app_perms_list = app_perms_list)
    return json.dumps(app_perms_list)

def form_delete_id_string(delete, is_form):
    # form the string 
    ids_string = "("
    if is_form:
        for i in range(0, len(delete)):
            if i != len(delete) - 1:
                ids_string += str(delete[i]) + ","
            else:
                ids_string += str(delete[i]) + ");"
    else:
        for i in range(0, len(delete)):
            if i != len(delete) - 1:
                ids_string += str(delete[i][0]) + ","
            else:
                ids_string += str(delete[i][0]) + ");"
    return ids_string


#==============================================================================#
@app.route('/admin_groups')
def admin_groups_run():
    # if the user is not logged in, redirect him/her to the login page
    #is_logged_in()

    # list of queries
    queries = []
    # get all the groups 
    queries.append("SELECT name FROM groups;")
    # create query to get the groups that the current user is a part of
    queries.append(
        "SELECT g.name FROM groups g "
        "INNER JOIN user_groups_relation ug ON ug.group_id = g.id "
        "WHERE ug.user_id = 1" + ";")

    # database connection to get the groups
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered=True)
        # get all the group names
        cur.execute(queries[0])
        group_names = cur.fetchall()

        # get all the group names for this user
        cur.execute(queries[1])
        admin_groups = cur.fetchall()        

        # close the connection
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if (conn):
            conn.close()
            print('Connection to db was closed!')

    # return the page with all the data stored in the groups variable which is a
    # dictionary with {name, yes/no} pairs
    groups = create_group_dict(group_names, admin_groups)
    #for key, value in groups.items():
    #    print(key + "-------" + value)
    #return render_template('admin_files/admin_groups.html', groups = groups)
    return json.dumps(groups)


def create_group_dict(group_names, admin_groups):
    groups = {}
    for group_row in group_names:
        if is_group_in_list(admin_groups, group_row[0]):
            groups[ group_row[0] ] = "Yes"
        else:
            groups[ group_row[0] ] = "No"
    return groups

def is_group_in_list(admin_groups, group):
    # verify if a specific group name is in the list or not
    for group_row in admin_groups:
        if group == group_row[0]:
            return True
    return False

#==============================================================================#
@app.route('/admin_add')
def admin_add_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

    return render_template('admin_files/admin_add_user.html') 

#==============================================================================#
###
# Redirect the user to the login page if it's not logged in
###
def is_logged_in():
    # if the user is not logged in, redirect him/her to the login page
    if not session.get('logged_in'):
        return render_template('common_files/login.html')

#==============================================================================#

@app.route('/', methods=['GET'])
def serve():
    return "yoyo", 200


if __name__ == "__main__":
  app.secret_key = os.urandom(12)
  app.run(debug=True, host='0.0.0.0', port=5000)