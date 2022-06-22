from crypt import methods
from telnetlib import STATUS
from urllib import response
from flask_restful import Resource, Api
from flask import make_response
from flask import Flask, flash, redirect, render_template, request, session, abort, flash, url_for, request, jsonify, make_response
from passlib.hash import sha256_crypt
import mysql.connector as mariadb
import make_response
import json
import os
#from backEnd import global_variables
from global_variables import *
from werkzeug.routing import BaseConverter
app = Flask(__name__, static_url_path="/static", template_folder="templates")
app.config["DEBUG"] = True

DB_HOST = '199.247.4.112'
DB_USER = 'sky_admin'
DB_PASSWORD = 'h^g8p{66TgW'
DB_DATABASE = 'sky_security'
DB_PORT = 3306

class IntListConverter(BaseConverter):
    regex = r'\d+(?:,\d+)*,?'

    def to_python(self, value):
        return [int(x) for x in value.split(',')]

    def to_url(self, value):
        return ','.join(str(x) for x in value)

class ListConverter(BaseConverter):
   # regex = r'\d+(?:,\d+)*,?'

    def to_python(self, value):
        return [x for x in value.split(',')]

    def to_url(self, value):
        return ','.join(str(x) for x in value)

app.url_map.converters['int_list'] = IntListConverter
app.url_map.converters['list'] = ListConverter
#==============================================================================#
@app.route('/admin_home/<int:user_id>')
def admin_home_run(user_id):
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
        "WHERE ug.user_id = " +str(user_id)  + ");")

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
#==============================================================================#
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
@app.route('/admin_groups/<int:user_id>')
def admin_groups_run(user_id):
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
        "WHERE ug.user_id = " + str(user_id) + ";")

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

#==============================================================================#
def create_group_dict(group_names, admin_groups):
    groups = {}
    for group_row in group_names:
        if is_group_in_list(admin_groups, group_row[0]):
            groups[ group_row[0] ] = "Yes"
        else:
            groups[ group_row[0] ] = "No"
    return groups
#==============================================================================#
def is_group_in_list(admin_groups, group):
    # verify if a specific group name is in the list or not
    for group_row in admin_groups:
        if group == group_row[0]:
            return True
    return False

#==============================================================================#
def create_query(groups, lista):
    query = ""
    user_name = str(lista[4])
    user_query = ( "INSERT INTO users (username, password, full_name, email, " 
    "phone_number, is_admin) VALUES ( '" + user_name + "' , '" + str(lista[3])
    + "', '" + str(lista[0]) + "', '" + str(lista[1]) + "', '" + str(lista[2]) + "', ")
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        user_id = "SELECT id FROM users WHERE username = '" + user_name + "' ;"
        cur = conn.cursor(buffered = True)

        if groups[0] == '1':
            user_query += "1);"
        else:
            user_query += "0);"
            
        cur.execute(user_query)
        conn.commit()

        cur.execute(user_id)
        user_id = str(cur.fetchone()[0])
        
        query = ("INSERT INTO user_groups_relation (user_id, group_id) VALUES ("
                 + str(user_id) + ", ")
        queries = []
        
        for i in range(0, len(groups)):
            queries.append(query + str(groups[i])+ ");")

        for i in range(0,len(queries)):
            cur.execute(str(queries[i]))
            conn.commit()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

    return query

#==============================================================================#
@app.route('/admin_settings/<int:user_id>', methods =['POST','GET'])
def admin_settings_run(user_id):
    #id from global_varibles gotten from login
    id = str(user_id)
    #username from global_varibles gotten from login
    #username= str(user_name[0]) 
    # database connection
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        #select all data from user where id matches
        query = "SELECT * from users WHERE id ='" + id + "';"
        cur.execute(query)
        query = cur.fetchone()
        cur.close()
        conn.close()

    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

    users = query
    users = jsonify(users)
    users.status_code = 200
    #return settings and display user`s information (id, full_name, email, phone_number)
    return users

#==============================================================================#
@app.route('/admin_settings_update/<int:user_id>', methods = ['POST'])
def admin_settings_update(user_id):
    # if the user is not logged in, redirect him/her to the login page
    #is_logged_in()

    #empty dictonary to store information about the user
    json_obj = request.json
    date_user = {}
    counter = 0
    
    if (json_obj.get("username")):
          date_user['username'] = json_obj.get("username")
          counter +=1
    else:
         date_user['username'] = 0
    if (json_obj.get("phone_number") and check_phone(str(json_obj.get('phone_number')))):
            date_user['phone_number'] = json_obj.get('phone_number')
            counter +=1
    elif not json_obj.get("phone_number"):
            date_user['phone_number'] = 0
    else:
            flash("Invalid phone number")
    if json_obj.get("full_name"):
            date_user['full_name'] = json_obj.get('full_name')
            counter +=1
    else:
         date_user['full_name'] = 0
    if json_obj.get('email') and check_email(str(json_obj.get('email'))):
            date_user['email'] = json_obj.get('email')
            counter +=1
    elif not json_obj.get('email'):
            date_user['email'] = 0
    else:
        flash("Not a valid email. Try again")
    if json_obj.get('password') and json_obj.get('new_password'):
        if json_obj.get('password') == json_obj.get('new_password'):
                date_user['password'] = sha256_crypt.hash(str(json_obj.get('password')))
                counter +=1
        else:
                flash("Password doesn`t match")
    elif not json_obj.get('password') :
            date_user['password'] = 0    
 
    sql = "UPDATE users SET "
    for key, value in date_user.items():
        if value != 0:
            sql += key + "= " + "'" + value + "'"
            sql += ","    

    # remove the last character ", "
    sql = sql[:-1]
    #update from id user
    sql += " WHERE id = " + str(user_id) + ";"
    # database connection
     
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)

        if counter!=0:
            cur.execute(sql)
            flash("Succesfully updated!")

        conn.commit()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

    return date_user
#==============================================================================#
@app.route('/add_user')
def admin_add_user():
    query1 = "SELECT id, name FROM groups ORDER BY id;"
    query2 = "SELECT id, name FROM permissions;"

    # database connection 
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        cur.execute(query1)
        groups = cur.fetchall()
        cur.execute(query2)
        perms = cur.fetchall()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')
    groups = json.dumps(groups)
    return groups
#==============================================================================#
@app.route('/submit_user/<int_list:groups>', methods = ['GET','POST'])
def submit_user_form(groups):
    #get the list of group/groups
    list_data = []
    json_obj = request.json

    print("in submit jsonobs == {}, groups = {}".format(json_obj, groups))

    if request.method == 'POST':
        if (json_obj.get('first_name')):
            full_name = str(json_obj.get('first_name')) + " " + str(json_obj.get('last_name'))
            list_data.append(full_name)

        if (json_obj.get('email')):
            if (check_email(str(json_obj.get('email')))):
                list_data.append(json_obj.get('email'))
            else:
                flash("Invalid email. Try again!")

        if (json_obj.get('phone_number')):
            if (check_phone(str(json_obj.get('phone_number')))):
                list_data.append(json_obj.get('phone_number'))
            else:
                flash("Invalid phone number!")

        if (json_obj.get('password') == json_obj.get('confirm_password')):
            list_data.append(sha256_crypt.hash(str(json_obj.get('password'))))
        else:
            flash("Password does not correspond. Try again!")

        if (json_obj.get('username') and check_username(str(json_obj.get('username')))):
            list_data.append(json_obj.get("username"))
        else:
            flash("Username already exist!")
                           
        
    create_query(groups, list_data)
    
    return json_obj
#==============================================================================#
def create_query(groups, lista):
    query = ""
    user_name = str(lista[4])
    user_query = ( "INSERT INTO users (username, password, full_name, email, " 
    "phone_number, is_admin) VALUES ( '" + user_name + "' , '" + str(lista[3])
    + "', '" + str(lista[0]) + "', '" + str(lista[1]) + "', '" + str(lista[2]) + "', ")
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        user_id = "SELECT id FROM users WHERE username = '" + user_name + "' ;"
        cur = conn.cursor(buffered = True)

        print("in create query groups[0] -- {}".format(groups[0]))

        if str(groups[0]) == "1":
            user_query += "1);"
        else:
            user_query += "0);"
        print(user_query)
        cur.execute(user_query)
        conn.commit()

        cur.execute(user_id)
        user_id = str(cur.fetchone()[0])
        
        query = ("INSERT INTO user_groups_relation (user_id, group_id) VALUES ("
                 + str(user_id) + ", ")
        queries = []
        
        for i in range(0, len(groups)):
            queries.append(query + str(groups[i])+ ");")

        for i in range(0,len(queries)):
            cur.execute(str(queries[i]))
            conn.commit()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

    return True
#==============================================================================#
@app.route('/getGroup', methods=['POST','GET'])
def admin_get_group():

    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)

    groups = "SELECT * from groups;"
    
    try:
        cur = conn.cursor(buffered = True)
        cur.execute(groups)
        groups = cur.fetchall()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')


    groups = json.dumps(groups)
    return  groups
#==============================================================================#
@app.route('/getUsers', methods=['POST','GET'])
def admin_get_users():

    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    users = "SELECT id, username from users;"

    try:
        cur = conn.cursor(buffered = True)
        cur.execute(users)
        users = cur.fetchall()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')


    users = json.dumps(users)
    return  users
#==============================================================================#
@app.route('/getPermissions', methods=['POST','GET'])
def admin_get_perms():

    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    permissions = "SELECT id, name from permissions;"

    try:
        cur = conn.cursor(buffered = True)
        cur.execute(permissions)
        permissions = cur.fetchall()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

    permissions = json.dumps(permissions)
    return  permissions
#==============================================================================#
@app.route('/getAllPermissions', methods=['POST','GET'])
def admin_get_allperms():

    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    permissions = "SELECT * from permissions;"

    try:
        cur = conn.cursor(buffered = True)
        cur.execute(permissions)
        permissions = cur.fetchall()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

    permissions = json.dumps(permissions)
    return  permissions
#==============================================================================#
@app.route('/getApps', methods=['POST','GET'])
def admin_get_apps():

    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    apps = "SELECT id,name from apps;"

    try:
        cur = conn.cursor(buffered = True)
        cur.execute(apps)
        apps = cur.fetchall()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

    apps = json.dumps(apps)
    return  apps
#==============================================================================#
@app.route('/getAllApps', methods=['POST','GET'])
def admin_get_AllApps():

    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    apps = "SELECT * from apps;"

    try:
        cur = conn.cursor(buffered = True)
        cur.execute(apps)
        apps = cur.fetchall()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

    apps = json.dumps(apps)
    return  apps
#==============================================================================#
@app.route('/add_group_run/<list:users>/<list:perms>', methods = ['POST'])
def insert_groups(users, perms):
    json_obj = request.json
    name = json_obj.get("name")
    description = json_obj.get("description")
    query = ("INSERT INTO groups (name, description) VALUES ('" + str(name) 
            + "', '" + str(description) + "');")
    query2 = "SELECT id from groups WHERE name = '" + str(name) +"';"
    
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        cur.execute(query)
        conn.commit()
        cur.execute(query2)
        query2 = cur.fetchone()[0]
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')
    insert_group_relation(query2, users)
    group_perm_relation(perms, query2)
    return json_obj
#==============================================================================#
def insert_group_relation(query, users):
    query2 = ("INSERT INTO user_groups_relation (group_id, user_id) VALUES (" 
                + str(query) + ",")
    queries = []
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        for i in range(0, len(users)):
            queries.append(query2 + str(users[i])+ ");")

        for i in range(0,len(queries)):
            cur.execute(str(queries[i]))
            conn.commit()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

    return True
#==============================================================================#
def group_perm_relation(perms, group_id):
    query = ("INSERT INTO groups_perm_relation (group_id, perm_id) VALUES (" 
            + str(group_id) + ", ")
    
    queries = []
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    
    try:
        cur = conn.cursor(buffered = True)
        for i in range(0, len(perms)):
            queries.append(query + str(perms[i])+ ");")
     
        for i in range(0,len(queries)):
            cur.execute(str(queries[i]))
            conn.commit()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

    return True
#==============================================================================#
@app.route('/add_perms_run/<list:id_groups>/<list:id_apps>', methods = ['GET', 'POST'])
def insert_perms(id_groups, id_apps):
    json_obj = request.json
    name = json_obj.get('name')
    description = json_obj.get('description')
    
    perm_id = "SELECT id from permissions"
    insert = ("INSERT INTO permissions (name, description, app_id) VALUES ('" 
                + str(name) + "', '" + str(description) + "', " )
    queries = []
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        for i in range(0, len(id_apps)):
            queries.append(insert + str(int(id_apps[i]))+ ");")
        for i in range(0,len(queries)):
            cur.execute(str(queries[i]))
            conn.commit()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')


    insert_groups_perm_relation(id_groups, name)
    return json_obj

#==============================================================================#
def insert_groups_perm_relation(group_id, name):

    query = "INSERT INTO groups_perm_relation (perm_id, group_id) VALUES (" 
    query2 = "SELECT id from permissions WHERE name= '" + str(name) + "';"
    queries = []
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    
   
    try:
        cur = conn.cursor(buffered = True)
        cur.execute(query2)
        query2 = cur.fetchone()[0]
        query += str(query2) + ", "
        for i in range(0, len(group_id)):
            queries.append(query + str(group_id[i])+ ");")
     
        for i in range(0,len(queries)):
            cur.execute(str(queries[i]))
            conn.commit()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

        return True
#==============================================================================#
@app.route('/add_apps_run', methods = ['POST'])
def insert_apps():
    json_obj = request.json
    name = json_obj.get('name')
    link = json_obj.get('link')
    insert = ("INSERT INTO apps (name, link) VALUES ('" + str(name) + "', '" 
                + str(link) + "');")
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        cur.execute(insert)
        conn.commit()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')
    return json_obj
#==============================================================================#
@app.route('/delete_user', methods = ['GET'])
def delete_user_run():
    users = []
    query = ("SELECT id, username, full_name, email, phone_number, is_admin " 
        "FROM users ORDER BY id;")

    # database connection to get the groups
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)

    try:
        cur = conn.cursor(buffered=True)
        
        # get all the usernames and fullnames
        cur.execute(query)
        users = cur.fetchall()

        # close the connection
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if (conn):
            conn.close()
            print('Connection to db was closed!')  
        
    data = json.dumps(users)
    return data
#==============================================================================#
@app.route('/delete_user_exec/<int_list:delete>', methods=['POST'])
def execute_delete_user(delete):
    # get the list of ids that the admin wants to delete
    #delete = request.form.getlist('checks')
    ids_string = form_delete_id_string(delete, True)    
    queries = []
    queries.append("DELETE FROM users WHERE id IN " + ids_string)

    # database connection to get the groups
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)

    try:
        cur = conn.cursor(buffered=True)
        
        # delete all the data related to the user/s
        cur.execute(queries[0])     
        conn.commit()

        # close the connection
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if (conn):
            conn.close()
            print('Connection to db was closed!')

    return str(ids_string)
    #return redirect("/delete_user")
#==============================================================================#
@app.route('/delete_group')
def delete_group_run():
    groups = []
    query = "SELECT * FROM groups ORDER BY id;"

    # database connection to get the groups
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)

    try:
        cur = conn.cursor(buffered=True)
        
        # get all the groups
        cur.execute(query)
        groups = cur.fetchall()

        # close the connection
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if (conn):
            conn.close()
            print('Connection to db was closed!')
    groups = json.dumps(groups)
    return groups            
#==============================================================================#
@app.route('/delete_group_exec/<int_list:delete>', methods = ['POST'])
def execute_delete_group(delete):
    ids_string = form_delete_id_string(delete, True)
    query = "DELETE FROM groups WHERE id IN " + ids_string + ";"
    
    # database connection to get the groups
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)

    try:
        cur = conn.cursor(buffered=True)

        # execute the query and commit the change
        cur.execute(query)
        conn.commit()

        # close the connection
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if (conn):
            conn.close()
            print('Connection to db was closed!')
    return str(ids_string)
#==============================================================================#
@app.route('/delete_perm')
def delete_perm_run():
    perms = []
    query = "SELECT * FROM permissions ORDER BY id;"

    # database connection to get the groups
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered=True)

        # get all the permissions
        cur.execute(query)
        perms = cur.fetchall()

        # close the connection
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if (conn):
            conn.close()
            print('Connection to db was closed!')
    perms = json.dumps(perms)
    return perms
#==============================================================================#
@app.route('/delete_perm_exec/<int_list:delete>', methods = ['POST'])
def execute_delete_perm(delete):
    ids_string = form_delete_id_string(delete, True)
    query = "DELETE FROM permissions WHERE id IN " + ids_string
    # database connection to get the groups
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)

    try:
        cur = conn.cursor(buffered=True)
        # execute the query and commit the change
        cur.execute(query)
        conn.commit()
        # close the connection
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if (conn):
            conn.close()
            print('Connection to db was closed!')    
    return str(ids_string)
#==============================================================================#
@app.route('/admin_group_modify/<int:user_id>', methods = ['GET'])
def getGroups(user_id):

    query = ("SELECT distinct g.* FROM groups g "
        "INNER JOIN user_groups_relation ug ON ug.group_id = g.id "
        "WHERE ug.user_id = " + str(user_id) + ";")

    try:
        conn = mariadb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
            database=DB_DATABASE, port=DB_PORT)
        cur = conn.cursor(buffered = True)
        cur.execute(query)
        groups = cur.fetchall()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()


    groups = json.dumps(groups)

    return groups
#==============================================================================#
@app.route('/admin_perms_modify/<int:user_id>', methods = ['GET'])
def getPermsMod(user_id):
    query = ("SELECT distinct p.* FROM permissions p "
        "INNER JOIN groups_perm_relation gp ON gp.perm_id = p.id "
        "WHERE gp.group_id IN ( "
        "SELECT g.id FROM groups g "
        "INNER JOIN user_groups_relation ug ON ug.group_id = g.id "
        "WHERE ug.user_id = " + str(user_id) + ");")
    try:
        conn = mariadb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
            database=DB_DATABASE, port=DB_PORT)
        cur = conn.cursor(buffered = True)
        cur.execute(query)
        perms = cur.fetchall()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()


    perms = json.dumps(perms)

    return perms    
#==============================================================================#
@app.route('/admin_modify', methods = ['POST', 'GET'])
def admin_modify_run():
    json_obj = request.json
    
    try:
        conn = mariadb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
            database=DB_DATABASE, port=DB_PORT)
        cur = conn.cursor(buffered = True)
        if 'id' in json_obj:
            #print(update_group(json_obj))
            cur.execute(update_group(json_obj))
        if 'id_perm' in json_obj:
            #print(update_permissions(json_obj))
            cur.execute(update_permissions(json_obj))
        if 'id_app' in json_obj:
            #print(update_apps(json_obj))
            cur.execute(update_apps(json_obj))

        #(insert_user_group, remove_user_group) = update_user_group(json_obj)    
        if ('id_user' and 'add_group') in json_obj:
            cur.execute(update_user_group(json_obj))
        if ('id_user' and 'remove_group') in json_obj:
            cur.execute(update_user_group(json_obj))
        
        #(insert_user_perm, remove_user_perm) = update_user_perm(json_obj)
        if ('id_group' and 'add_perm') in json_obj:
            cur.execute(update_user_perm(json_obj))
        if ('id_group' and 'remove_perm') in json_obj:
            cur.execute(update_user_perm(json_obj))

        conn.commit()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
    return json_obj
#==============================================================================#
# The actual function for update data in groups
def update_group(modify):
    update_query = ""
    id = modify.get('id')
    name = modify.get('name')
    description = modify.get('description')
    
    if (modify.get('id') and modify.get('name')) != None or \
    (modify.get('id') and modify.get('description')) != None: 
        update_query = "UPDATE groups"
        if modify.get('name') != "" and modify.get('description') != "":
            update_query += " SET name = \'" + name + '\', description = \''\
            + description + '\''
        if modify.get('description') == "":
            update_query += " SET name = \'" + name + '\''
        if modify.get('name') == "":
            update_query += " SET description = \'" +  description + '\''
        update_query += " WHERE id = " + id + ';'
    return update_query
#==============================================================================#
# The actual function for update data in permissions
def update_permissions(modify):
    update_query = ""
    id_perm = modify.get('id_perm')
    name_perm = modify.get('name_perm')
    desc_perm = modify.get('desc_perm')
    app = modify.get('app')

    if (modify.get('id_perm') and modify.get('id_perm')) != "" or \
    (modify.get('id_perm') and modify.get('desc_perm')) != "" or \
    (modify.get('id_perm') and modify.get('app')!= ""): 
        update_query = "UPDATE permissions"
        if modify.get('name_perm') != "" and modify.get('desc_perm') != "" and modify.get('app') != "":
            update_query += " SET name = \'" + name_perm + '\', description = \''\
            + desc_perm + '\' , app_id = \''  + app + '\''
        if modify.get('desc_perm') == "":
            update_query += " SET name = \'" + name_perm + '\''
        if modify.get('name_perm') == "":
            update_query += " SET description = \'" + desc_perm + '\''
        update_query += " WHERE id = " + id_perm + ';'
    return update_query
#==============================================================================#
# The actual function for update data in apps
def update_apps(modify):
    update_query = ""
    id_app = modify.get('id_app')
    name_app = modify.get('name_app')
    link = modify.get('link')
    if (modify.get('id_app') and modify.get('name_app')) != "" or \
    (modify.get('id_app') and modify.get('link')) != "": 
        update_query = "UPDATE apps"
        if modify.get('name_app') != "" and modify.get('link') != "":
            update_query += " SET name = \'" + name_app + '\', link = \''\
            + link + '\''
        if modify.get('link') == "":
            update_query += " SET name = \'" + name_app + '\''
        if modify.get('name_app') == "":
            update_query += " SET link = \'" + link + '\''
        update_query += " WHERE id = " + id_app + ';'
    return update_query
#==============================================================================#
def update_user_group(modify):
    insert_query = ''
    remove_query = ''
    id_user = modify.get('id_user')
    add_group = modify.get('add_group')
    remove_group = modify.get('remove_group')

    if (modify.get('id_user') and modify.get('add_group') != ""):
        insert_query +=("Insert into user_groups_relation(user_id, group_id) "
        "values(" + id_user + ", " + add_group + ");")
    elif (modify.get('id_user') and modify.get('remove_group') != ""):
        remove_query += ("DELETE FROM user_groups_relation "
        "WHERE user_id = " + id_user + " and group_id = " + remove_group + ";")
    if insert_query != '':
        return insert_query
    elif remove_query != '':
        return remove_query   
#==============================================================================#
def update_user_perm(modify):
    insert_query = ''
    remove_query = ''
    id_group = modify.get('id_group')
    add_perm = modify.get('add_perm')
    remove_perm = modify.get('remove_perm')

    if (modify.get('id_group') and modify.get('add_perm')) != "":
        insert_query +=("Insert into groups_perm_relation(group_id, perm_id) "
        "values(" + id_group + ", " + add_perm + ");")
    elif (modify.get('id_group') and modify.get('remove_perm')) != "":
        remove_query += ("DELETE FROM groups_perm_relation "
        "WHERE group_id = " + id_group + " and perm_id = " + remove_perm + ";")
    if insert_query != '':
        return insert_query
    elif remove_query != '':
        return remove_query
#==============================================================================#
@app.route('/delete_app')
def delete_app_run():

    apps = []
    query = "SELECT * FROM apps ORDER BY id;"
    # database connection to get the apps
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered=True)
        # get all the permissions
        cur.execute(query)
        apps = cur.fetchall()
        # close the connection
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if (conn):
            conn.close()
            print('Connection to db was closed!')
    apps = json.dumps(apps)        
    return apps             
#==============================================================================#
@app.route('/delete_app_exec/<int_list:delete>', methods = ['POST'])
def execute_delete_app(delete):

    ids_string = form_delete_id_string(delete, True)
    query = "DELETE FROM apps WHERE id IN " + ids_string
    # database connection to execute the query
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)

    try:
        cur = conn.cursor(buffered=True)

        # execute the query and commit the change
        cur.execute(query)
        conn.commit()

        # close the connection
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if (conn):
            conn.close()
            print('Connection to db was closed!')
    return str(ids_string)    
#==============================================================================#
@app.route('/user_home/<int:user_id>')
def user_home_run(user_id):  
    # list of queries
    queries = []
    app_perms_list = {}

    # create query to get the pemissions of the user based on the groups that
    # the user is a part of
    queries.append(
        "SELECT * FROM permissions p "
        "INNER JOIN groups_perm_relation gp ON gp.perm_id = p.id "
        "WHERE gp.group_id IN ( "
        "SELECT g.id FROM groups g "
        "INNER JOIN user_groups_relation ug ON ug.group_id = g.id "
        "WHERE ug.user_id = " + str(user_id) + ");")

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
    return json.dumps(app_perms_list)
#==============================================================================#
@app.route('/user_groups/<int:user_id>')
def user_groups_run(user_id):
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
        "WHERE ug.user_id = " + str(user_id) + ";")

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
    return json.dumps(groups)
#==============================================================================#
@app.route('/user_settings/<int:user_id>', methods =['POST','GET'])
def user_settings_run(user_id):
    #id from global_varibles gotten from login
    id = str(user_id)
    #username from global_varibles gotten from login
    #username= str(user_name[0]) 
    # database connection
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        #select all data from user where id matches
        query = "SELECT * from users WHERE id ='" + id + "';"
        cur.execute(query)
        query = cur.fetchone()
        cur.close()
        conn.close()

    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

    users = query
    users = jsonify(users)
    users.status_code = 200
    #return settings and display user`s information (id, full_name, email, phone_number)
    return users
#==============================================================================#
@app.route('/user_settings_update/<int:user_id>', methods = ['POST', 'GET'])
def user_settings_update(user_id):
    json_obj = request.json
    date_user = {}
    counter = 0
    
    if (json_obj.get("username")):
          date_user['username'] = json_obj.get("username")
          counter +=1
    else:
         date_user['username'] = 0
    if (json_obj.get("phone_number") and check_phone(str(json_obj.get('phone_number')))):
            date_user['phone_number'] = json_obj.get('phone_number')
            counter +=1
    elif not json_obj.get("phone_number"):
            date_user['phone_number'] = 0
    else:
            flash("Invalid phone number")
    if json_obj.get("full_name"):
            date_user['full_name'] = json_obj.get('full_name')
            counter +=1
    else:
         date_user['full_name'] = 0
    if json_obj.get('email') and check_email(str(json_obj.get('email'))):
            date_user['email'] = json_obj.get('email')
            counter +=1
    elif not json_obj.get('email'):
            date_user['email'] = 0
    else:
        flash("Not a valid email. Try again")
    if json_obj.get('password') and json_obj.get('new_password'):
        if json_obj.get('password') == json_obj.get('new_password'):
                date_user['password'] = sha256_crypt.hash(str(json_obj.get('password')))
                counter +=1
        else:
                flash("Password doesn`t match")
    elif not json_obj.get('password') :
            date_user['password'] = 0    
 
    sql = "UPDATE users SET "
    for key, value in date_user.items():
        if value != 0:
            sql += key + "= " + "'" + value + "'"
            sql += ","    

    # remove the last character ", "
    sql = sql[:-1]
    #update from id user
    sql += " WHERE id = " + str(user_id) + ";"
    # database connection
     
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)

        if counter!=0:
            cur.execute(sql)
            flash("Succesfully updated!")

        conn.commit()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

    return date_user
#==============================================================================#
@app.route('/', methods=['GET'])
def serve():
    return "yoyo", 200


if __name__ == "__main__":
  app.secret_key = os.urandom(12)
  app.run(debug=True, host='0.0.0.0', port=5000)