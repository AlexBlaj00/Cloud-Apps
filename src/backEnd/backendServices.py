from flask_restful import Resource, Api
from flask import Flask, flash, redirect, render_template, request, session, abort, flash, url_for, request, jsonify
from passlib.hash import sha256_crypt
import mysql.connector as mariadb
import json
import os
from global_variables import *
app = Flask(__name__, static_url_path="/static", template_folder="templates")
app.config["DEBUG"] = True

DB_HOST = '199.247.4.112'
DB_USER = 'sky_admin'
DB_PASSWORD = 'h^g8p{66TgW'
DB_DATABASE = 'sky_security'
DB_PORT = 3306

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
    #users = json.dumps(users)
    #users = users.split(" ")
    #print(users)
    #for i in users: 
    #    print(i)
   # print(type(users))
    users = jsonify(users)
    users.status_code = 200
    #print(type(users))
    #return settings and display user`s information (id, full_name, email, phone_number)
    return users
#==============================================================================#
@app.route('/user_settings_update/<int:user_id>', methods = ['POST', 'GET'])
def user_settings_update(user_id):
    # if the user is not logged in, redirect him/her to the login page
    #is_logged_in()
    print(" IN BACKEND USER SETTINGS UPDATE")
    #empty dictonary to store information about the user
    #username = request.form['username']
    #full_name = request.form['full_name']
    #phone_number = request.form['phone_number']
    #email = request.form.get('email')
    #password = request.form['password']
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

    print(date_user)
    return date_user
#==============================================================================#
@app.route('/', methods=['GET'])
def serve():
    return "yoyo", 200


if __name__ == "__main__":
  app.secret_key = os.urandom(12)
  app.run(debug=True, host='0.0.0.0', port=5000)