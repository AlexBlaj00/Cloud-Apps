from contextlib import nullcontext
import os
from os.path import join, dirname, realpath
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, Response, send_file, make_response
import mysql.connector as mariadb
from passlib.hash import sha256_crypt
import csv, io, time, zipfile, os
from os.path import basename
from zipfile import ZipFile
from global_variables import *
import numpy as np
import plotly
import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.offline import init_notebook_mode
import pandas as pd
import json
import plotly.express as px
import pandas as pd
from services import adminServices
UPLOAD_FOLDER = 'static/files/'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER


#==============================================================================#
@app.route('/admin_home')
def admin_home_run():
   # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

    # list of queries
    queries = []

    # create query to get the pemissions of the user based on the groups that
    # the user is a part of
    queries.append(
        "SELECT * FROM permissions p "
        "INNER JOIN groups_perm_relation gp ON gp.perm_id = p.id "
        "WHERE gp.group_id IN ( "
        "SELECT g.id FROM groups g "
        "INNER JOIN user_groups_relation ug ON ug.group_id = g.id "
        "WHERE ug.user_id = " + str(user_id[0]) + ");")

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
    return render_template('admin_files/admin_home.html', app_perms_list = app_perms_list)
#==============================================================================#
@app.route('/admin_groups')
def admin_groups_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()
    id = user_id
    groups = adminServices.login(id)
    return render_template('admin_files/admin_groups.html', groups = groups
        )
#==============================================================================#
def get_user(user):
  #id_user = str(user[0][0])
  #print(str(user[0][0]))
  query = "SELECT id FROM users WHERE id=" + str(user[0][0]) + ";"
  conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
  try:
        cur = conn.cursor(buffered=True)
        cur.execute(query)
        users = cur.fetchall()
        cur.close()
        conn.close()
  except mariadb.Error as error:
            print("Failed to read data from table", error)
  finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

  return users
#==============================================================================#
@app.route('/admin_add')
def admin_add_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

    return render_template('admin_files/admin_add_user.html')    
#==============================================================================#
@app.route('/admin_modify', methods = ['POST', 'GET'])
def admin_modify_run():
    modify = request.form
    query = ("SELECT distinct g.* FROM groups g "
        "INNER JOIN user_groups_relation ug ON ug.group_id = g.id "
        "WHERE ug.user_id = " + str(user_id[0]) + ";")
    query2 = (
        "SELECT distinct p.* FROM permissions p "
        "INNER JOIN groups_perm_relation gp ON gp.perm_id = p.id "
        "WHERE gp.group_id IN ( "
        "SELECT g.id FROM groups g "
        "INNER JOIN user_groups_relation ug ON ug.group_id = g.id "
        "WHERE ug.user_id = " + str(user_id[0]) + ");")
    query3 = "Select id, username from users;"
    query4 = "Select * from apps;"
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()
    try:
        conn = mariadb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
            database=DB_DATABASE, port=DB_PORT)
        cur = conn.cursor(buffered = True)
        (groups, perm, users, apps) = temp(query, query2, query3, query4)
        if request.method == 'POST':
                if update_group(modify) != '':
                    cur.execute(update_group(modify))
                if update_permissions(modify) != '':
                    cur.execute(update_permissions(modify))
                if update_apps(modify) != '':
                    cur.execute(update_apps(modify))
                (insert_user_group, remove_user_group) = update_user_group(modify)
                if insert_user_group != '':
                    cur.execute(insert_user_group)
                if remove_user_group != '':
                    cur.execute(remove_user_group)
                (insert_user_perm, remove_user_perm) = update_user_perm(modify)
                if insert_user_perm != '':
                    cur.execute(insert_user_perm)
                if remove_user_perm != '':
                    cur.execute(remove_user_perm)
                conn.commit()
        elif request.method == 'GET':
            return render_template('admin_files/admin_modify.html', groups = groups, perm = perm, users = users, apps = apps)
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
    (groups, perm, users, apps) = temp(query, query2, query3, query4)
    return render_template('admin_files/admin_modify.html', groups = groups, perm = perm,  users = users, apps = apps)
#==============================================================================#
# use this function to get groups and permission, without reloading the page
def temp(query, query2, query3, query4):
    groups = ''
    permissions = ''
    users = ''
    apps = ''
    try: 
        conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
        cur = conn.cursor(buffered = True)
        cur.execute(query)
        groups = cur.fetchall()
        cur.execute(query2)
        permissions = cur.fetchall()
        cur.execute(query3)
        users = cur.fetchall()
        cur.execute(query4)
        apps = cur.fetchall()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
    return (groups, permissions, users, apps)
#==============================================================================#
# The actual function for update data in groups
def update_group(modify):
    update_query = ""
    if (modify.get('id') and modify.get('name')) or \
    (modify.get('id') and modify.get('description')): 
        update_query = "UPDATE groups"
        if modify.get('name') != '' and modify.get('description') != '':
            update_query += " SET name = \'" + modify['name'] + '\', description = \''\
            + modify['description'] + '\''
        if modify.get('description') == '':
            update_query += " SET name = \'" + modify['name'] + '\''
        if modify.get('name') == '':
            update_query += " SET description = \'" + modify['description'] + '\''
        update_query += " WHERE id = " + modify['id'] + ';'
    return update_query
#==============================================================================#
# The actual function for update data in permissions
def update_permissions(modify):
    update_query = ""
    if (modify.get('id_perm') and modify.get('name_perm')) or \
    (modify.get('id_perm') and modify.get('desc_perm')) or \
    (modify.get('id_perm') and modify.get('app')): 
        update_query = "UPDATE permissions"
        if modify.get('name_perm') != '' and modify.get('desc_perm') != '' and modify.get('app'):
            update_query += " SET name = \'" + modify['name_perm'] + '\', description = \''\
            + modify['desc_perm'] + '\' , app_id = \''  + modify['app'] + '\''
        if modify.get('desc_perm') == '':
            update_query += " SET name = \'" + modify['name_perm'] + '\''
        if modify.get('name_perm') == '':
            update_query += " SET description = \'" + modify['desc_perm'] + '\''
        update_query += " WHERE id = " + modify['id_perm'] + ';'
    return update_query
#==============================================================================#
# The actual function for update data in apps
def update_apps(modify):
    update_query = ""
    if (modify.get('id_app') and modify.get('name_app')) or \
    (modify.get('id_app') and modify.get('link')): 
        update_query = "UPDATE apps"
        if modify.get('name_app') != '' and modify.get('link') != '':
            update_query += " SET name = \'" + modify['name_app'] + '\', link = \''\
            + modify['link'] + '\''
        if modify.get('link') == '':
            update_query += " SET name = \'" + modify['name_app'] + '\''
        if modify.get('name_app') == '':
            update_query += " SET link = \'" + modify['link'] + '\''
        update_query += " WHERE id = " + modify['id_app'] + ';'
    return update_query
#==============================================================================#
def update_user_group(modify):
    insert_query = ''
    remove_query = ''
    if (modify.get('id_user') and modify.get('add_group')):
        insert_query +=("Insert into user_groups_relation(user_id, group_id) "
        "values(" + modify['id_user'] + ", " + modify['add_group'] + ");")
    elif (modify.get('id_user') and modify.get('remove_group')):
        remove_query += ("DELETE FROM user_groups_relation "
        "WHERE user_id = " + modify['id_user'] + " and group_id = " + modify['remove_group'] + ";")
    return (insert_query, remove_query)
#==============================================================================#
def update_user_perm(modify):
    insert_query = ''
    remove_query = ''
    if (modify.get('id_group') and modify.get('add_perm')):
        insert_query +=("Insert into groups_perm_relation(group_id, perm_id) "
        "values(" + modify['id_group'] + ", " + modify['add_perm'] + ");")
    elif (modify.get('id_group') and modify.get('remove_perm')):
        remove_query += ("DELETE FROM groups_perm_relation "
        "WHERE group_id = " + modify['id_group'] + " and perm_id = " + modify['remove_perm'] + ";")
    return (insert_query, remove_query)
#==============================================================================#
@app.route('/delete_user')
def delete_user_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

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
    
    return render_template('admin_files/admin_delete_user.html', users = users)
    
@app.route('/delete_user_exec', methods=['POST'])
def execute_delete_user():
    # get the list of ids that the admin wants to delete
    delete = request.form.getlist('checks')

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

    return redirect("/delete_user")
    

#==============================================================================#

@app.route('/delete_group')
def delete_group_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

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

    return render_template('admin_files/admin_delete_group.html', groups = groups)

@app.route('/delete_group_exec', methods = ['POST'])
def execute_delete_group():
    # get the list of ids that the admin wants to delete
    delete = request.form.getlist('checks')

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
    
    return redirect("/delete_group")

#==============================================================================#

@app.route('/delete_perm')
def delete_perm_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

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

    return render_template('admin_files/admin_delete_perm.html', perms = perms)

#==============================================================================#

@app.route('/delete_perm_exec', methods=['POST'])
def execute_delete_perm():
     # get the list of ids that the admin wants to delete
    delete = request.form.getlist('checks')

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
            
    return redirect('/delete_perm')

#==============================================================================#

@app.route('/delete_app')
def delete_app_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

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

    return render_template('admin_files/admin_delete_app.html', apps = apps)

#==============================================================================#

@app.route('/delete_app_exec', methods=['POST'])
def execute_delete_app():
     # get the list of ids that the admin wants to delete
    delete = request.form.getlist('checks')

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
            
    return redirect('/delete_app')

#==============================================================================#

@app.route('/admin_msg')
def admin_msg_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

    return render_template('admin_files/admin_msg.html')

#==============================================================================#

@app.route('/admin_forum')
def admin_forum_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

    return render_template('admin_files/admin_forum.html')

#==============================================================================#

@app.route('/admin_settings', methods =['POST','GET'])
def admin_settings_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

    #id from global_varibles gotten from login
    id = str(user_id[0])
    #username from global_varibles gotten from login
#    username= str(user_name[0]) 
    #select all data from user where id matches
    query = "SELECT * from users WHERE id ='" + id + "';"

    # database connection 
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        cur.execute(query)
        query = cur.fetchall()
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')

    #return settings and display user`s information (id, full_name, email, phone_number)
    return render_template('admin_files/admin_settings.html', users = query)

#==============================================================================#

@app.route('/admin_settings_update', methods = ['POST'])
def admin_settings_update():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

    #empty dictonary to store information about the user
    date_user = {}
#    username = str(user_name[0])
    id = str(user_id[0])
    counter = 0
    # site method for update form is POST
    if request.method == 'POST':
        if request.form.get('full_name'):
            #if user completed full_name field it will be added to dictonary
            date_user['full_name'] = request.form.get('full_name')
            counter +=1
        if request.form.get('username'):
            date_user['username'] = request.form.get('username')
            counter +=1
        else: 
            date_user['username'] = 0
        if request.form.get('phone_number') and check_phone(request.form.get('phone_number')):
            date_user['phone_number'] = request.form.get('phone_number')
            counter +=1
        elif not request.form.get('phone_number'):
            date_user['phone_number'] = 0
        else:
             flash("Invalid phone number")
        if request.form.get('email') and check_email(request.form.get('email')) :
            date_user['email'] = request.form.get('email')
            counter +=1
        elif not request.form.get('email'):
            date_user['email'] = 0
        else:
            flash("Not a valid email. Try again.")
        if request.form.get('password') and  request.form.get('new_password'):
            if request.form.get('password') == request.form.get('new_password'):
                date_user['password'] = sha256_crypt.hash(request.form.get('password'))
                counter +=1
            else:
                flash("Password doesn`t match")
        elif not request.form.get('password') and not request.form.get('new_password'):
            date_user['password'] = 0
        
    
    sql = "UPDATE users SET "
    # looping throught dictonary and create the query to find which dates must be updated
    for key, value in date_user.items():
        if value != 0:
            sql += key + "= " + "'" + value + "'" 
            sql += ","
    
    # remove the last character ", "
    sql = sql[:-1]
    #update from id user
    sql += " WHERE id = " + id + ";" 

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

    return redirect("/admin_settings")

#==============================================================================#

@app.route('/admin_contact')
def admin_contact_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()
    
    return render_template('admin_files/admin_contact.html')

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

    return render_template('admin_files/admin_add_user.html', groups = groups, 
                            perms = perms)

#==============================================================================#

@app.route('/submit_user', methods = ['GET','POST'])
def submit_user_form():
    #get the list of group/groups
    g = request.form.getlist('groups')
    
    l = []
    print(g)
    print('-----')
    
    if request.method == 'POST':
        full_name = (str(request.form.get('first_name')) + " "
                     + str(request.form.get('last_name')))
        l.append(full_name)
        print(full_name)
        print('-----')
        if check_email(request.form.get('email')):
            l.append(request.form.get('email'))
            print(request.form.get('email'))
        else:
            flash("Invalid email. Try again!")
        if check_phone(request.form.get('phone_number')):
            l.append(request.form.get('phone_number'))
            print(request.form.get('phone_number'))
        else:
            flash("Invalid phone number. Try again!")
        if request.form.get('password') == request.form.get('confirm_password'):
            l.append(sha256_crypt.hash(request.form.get('password')))
        else:
            flash('Password does not correspond. Try again!')
        if check_username(request.form.get('username')) == True:
            l.append(request.form.get('username'))
        else:
            flash("Username already exist!")
            return redirect('/add_user')

 
    print(l)
    if len(l) == 5 and g:
        flash("Succesfully created user!")
    create_query(g, l)
    return redirect('/add_user')

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
            #query += str(groups[i]) + ");"
            #queries.append(query)
            #query = query[:-3]
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
def check_username(username):
    check = True
    user_query = "SELECT username FROM users;"
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        cur.execute(user_query)
        user_query = cur.fetchall()
        for i in user_query:
            if i[0] == username:
                check = False
                break
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')
    
    return check
#==============================================================================#

@app.route('/add_group', methods=['POST','GET'])
def admin_add_group():

    #print('\n\n\n\n'+str(user_id[0])+'\n\n\n\n')
    query = ("SELECT * from groups;")
    query2 = "SELECT id, username from users;"
    query3 = "SELECT id, name from permissions;"
    (groups, users, permissions)= query_for_user_groups_relation(query, query2, query3)
    #insert_groups()
    
    # insert into groups_perm_relation group id nou creat + perm id selectat
    return render_template('admin_files/admin_add_group.html', groups = groups, 
                            users = users, permissions = permissions)
#==============================================================================#
def query_for_user_groups_relation(query, query2, query3):
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        cur.execute(query)
        query = cur.fetchall()
        cur.execute(query2)
        query2 = cur.fetchall()
        cur.execute(query3)
        query3 = cur.fetchall()
        
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')
    return (query, query2, query3)
#==============================================================================#
@app.route('/add_group_run', methods = ['POST'])
def insert_groups():
    add = request.form
    name = add.get('name')
    description = add.get('description')
    users = request.form.getlist('users')
    perms = request.form.getlist('permissions')
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
    return redirect('/add_group')
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
    return redirect('/add_group_run')

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
@app.route('/add_perms', methods = ['POST','GET'])
def admin_add_perms():
    query = "SELECT * from permissions;"
    groups = "SELECT * from groups;"
    apps = "SELECT id, name from apps"
    (query, groups, apps) = exec_query(query, groups, apps)
    return render_template('admin_files/admin_add_perm.html', perms = query, 
                            groups = groups, apps = apps)
#==============================================================================#
def exec_query(query1, query2, query3):
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        cur = conn.cursor(buffered = True)
        cur.execute(query1)
        query1 = cur.fetchall()
        cur.execute(query2)
        query2 = cur.fetchall()
        cur.execute(query3)
        query3 = cur.fetchall()
        
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if conn:
            conn.close()
            print('Connection to db was closed!')
    return (query1, query2, query3)
#==============================================================================#
@app.route('/add_perms_run', methods = ['POST'])
def insert_perms():
    add_perms = request.form
    name = add_perms.get('name')
    description = add_perms.get('description')
    id_apps = add_perms.getlist('apps')
    id_groups = add_perms.getlist('groups')
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

    #group_id = id_groups
    # name = id
    insert_groups_perm_relation(id_groups, name)
    return redirect('/add_perms')
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
@app.route('/add_apps')
def add_apps_load():
    apps = "SELECT * from apps"
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
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
    return render_template('admin_files/admin_add_app.html', apps = apps)
#==============================================================================#
@app.route('/add_apps_run', methods = ['POST'])
def insert_apps():
    apps = request.form
    name = apps.get('name')
    link = apps.get('link')
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
    return redirect ('/add_apps')
#==============================================================================#
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


    return render_template('admin_files/admin_dashboard.html', 
        graphJSON = graphJSON, graphJSON2=graphJSON2, graphJSON3 = graphJSON3)
#==============================================================================#
@app.route('/import_export')
@app.route('/import_export/<b>')
def imp_exp_load(b = ''):
    return render_template('admin_files/admin_imp_exp.html', button = b)
#------------------------------------------------------------------------------#
def zipFilesInDir(dirName, zipFileName, filter):
   # create a ZipFile object
   with ZipFile(zipFileName, 'w') as zipObj:
       # Iterate over all the files in directory
       for folderName, subfolders, filenames in os.walk(dirName):
           for filename in filenames:
               if filter(filename):
                   # create complete filepath of file in directory
                   filePath = os.path.join(folderName, filename)
                   # Add file to zip
                   zipObj.write(filePath, basename(filePath))
#------------------------------------------------------------------------------#
@app.route('/export_data_run', methods=['POST'])
def export_data():
    # Table headers
    USERS_HEADER = ['id', 'username', 'password', 'full_name', 'email', 
                    'phone_number', 'is_admin']
    GROUPS_HEADER = ['id', 'name', 'description']
    PERMS_HEADER = ['id', 'name', 'description', 'app_id']
    APPS_HEADER = ['id', 'name', 'link']
    USERS_GROUPS_HEADER = ['id', 'user_id', 'group_id']
    APPS_PERMS_HEADER = ['id', 'group_id', 'perm_id']

    # download button
    b = ''

    # get the list of objects that the admin wants to export
    export = request.form.getlist('checks_exp')

    if export:
        # if it's not empty, then run the queries
        conn = mariadb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
            database=DB_DATABASE, port=DB_PORT)
        query = 'SELECT * FROM '
        try:
            cur = conn.cursor(buffered = True)
            for table in export:
                print("table name: " + table)
                tmp_query = query + table + ';'
                print("Query: " + tmp_query)
                cur.execute(tmp_query)
                table_data = cur.fetchall()                
                print(table_data)
                if table == 'users':
                    with open('./static/export/users.csv', 'w+') as file:
                        writer = csv.writer(file)
                        writer.writerow(USERS_HEADER)
                        writer.writerows(table_data)
                        print('-----users')
                elif table == 'groups':
                    with open('./static/export/groups.csv', 'w+') as file:
                        writer = csv.writer(file)
                        writer.writerow(GROUPS_HEADER)
                        writer.writerows(table_data)
                        print('-----groups')
                elif table == 'permissions':
                    with open('./static/export/permissions.csv', 'w+') as file:
                        writer = csv.writer(file)
                        writer.writerow(PERMS_HEADER)
                        writer.writerows(table_data)
                        print('-----perms')
                elif table == 'apps':
                    with open('./static/export/apps.csv', 'w+') as file:
                        writer = csv.writer(file)
                        writer.writerow(APPS_HEADER)
                        writer.writerows(table_data)
                        print('-----apps')
                elif table == 'user_groups_relation':
                    with open('./static/export/user_groups_relation.csv', 'w+') as file:
                        writer = csv.writer(file)
                        writer.writerow(USERS_GROUPS_HEADER)
                        writer.writerows(table_data)
                        print('-----u_g_rel')
                elif table == 'group_perm_relation':
                    with open('./static/export/group_perm_relation.csv', 'w+') as file:
                        writer = csv.writer(file)
                        writer.writerow(APPS_PERMS_HEADER)
                        writer.writerows(table_data)     
                        print('-----g_p_rel')
            cur.close()
            conn.close()
        except mariadb.Error as error:
                print("Failed to read data from table", error)
        finally:
            if conn:
                conn.close()
                print('Connection to db was closed!')
        # create a zip archive of all the csv files
        zipFilesInDir('./static/export', 'export_data.zip', 
                lambda name : 'csv' in name)
        # create download button to be inserted into page
        b = 'show button'
    return redirect('/import_export/{b}')
#------------------------------------------------------------------------------#
@app.route('/export_data_download')
def export_data_download():
    output = os.system("rm -rf ./static/export/*")
    print("command output" + output)
    # Changed line below
    return send_file('./export_data.zip', as_attachment=True)
#------------------------------------------------------------------------------#
@app.route('/import_data_run', methods=['POST'])
def import_data():
    uploaded_file = request.files['import_csv']
    
    if uploaded_file.filename != '':
        file_path = UPLOAD_FOLDER + uploaded_file.filename
        # set the file path
        uploaded_file.save(file_path)
        parseCSV(file_path)
        # save the file
    return redirect('import_export')
#==============================================================================#
def parseCSV(filePath):
    USERS_HEADER = ['id', 'username', 'password', 'full_name', 'email', 
                    'phone_number', 'is_admin']
    GROUPS_HEADER = ['id', 'name', 'description']
    PERMS_HEADER = ['id', 'name', 'description', 'app_id']
    APPS_HEADER = ['id', 'name', 'link']
    USERS_GROUPS_HEADER = ['id', 'user_id', 'group_id']
    APPS_PERMS_HEADER = ['id', 'group_id', 'perm_id']
    imported = request.form.getlist('checks_imp')
    print(str(imported))
    
    conn = mariadb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
            database=DB_DATABASE, port=DB_PORT)
   
    
    if str(imported[0]) == 'users':
        csvData = pd.read_csv(filePath, names=USERS_HEADER, header=None)
        for i, row in csvData.iterrows():
            if row[0] == 'id':
                continue
            sql = "INSERT INTO users (id, username, password, full_name, email, phone_number, id_admin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (row['id'], row['username'], row['password'], row['full_name'], row['email'], row['phone_number'], row['id_admin'])
            try:
                cur = conn.cursor(buffered = True)
                cur.execute(sql, values)
                conn.commit()
                print(i, row['id'], row['username'], row['password'], row['full_name'], row['email'], row['phone_number'], row['id_admin'])
                cur.close()
                conn.close()
            except mariadb.Error as error:
                print("Failed to read data from table", error)
            finally:
                if conn:
                    conn.close()
                    print('Connection to db was closed!')
    
    elif str(imported[0]) == 'groups':
        csvData = pd.read_csv(filePath, names=GROUPS_HEADER, header=None)
        for i, row in csvData.iterrows():
            if row[0] == 'id':
                continue
            sql = "INSERT INTO groups (id, name, description) VALUES (%s, %s, %s)"
            values = [row['id'], row['name'], row['description']]
            try:
                cur = conn.cursor(buffered = True)
                cur.execute(sql, (values))
                conn.commit()
                print(i, row['id'], row['name'], row['description'])
                cur.close()
                conn.close()
            except mariadb.Error as error:
                print("Failed to read data from table", error)
            finally:
                if conn:
                    conn.close()
                    print('Connection to db was closed!')
      
    elif str(imported[0]) == 'permissions':
        csvData = pd.read_csv(filePath, names=PERMS_HEADER, header=None)
        for i, row in csvData.iterrows():
            sql = "INSERT INTO permissions (id, name, description, app_id) VALUES (%s, %s, %s, %s)"
            values = [row['id'], row['name'], row['description'], row['app_id']]
            try:
                cur = conn.cursor(buffered = True)
                cur.execute(sql, (values))
                conn.commit()
                print(i, row['id'], row['name'], row['description'], row['app_id'])
                cur.close()
                conn.close()
            except mariadb.Error as error:
                print("Failed to read data from table", error)
            finally:
                if conn:
                    conn.close()
                    print('Connection to db was closed!')
    elif str(imported[0]) == 'apps':
        csvData = pd.read_csv(filePath, names=APPS_HEADER, header=None)
        for i, row in csvData.iterrows():
            if row[0] == 'id':
                continue
            sql = "INSERT INTO apps (id, name, link) VALUES (%s, %s, %s)"
            values = [row['id'], row['name'], row['link']]
            try:
                cur = conn.cursor(buffered = True)
                cur.execute(sql, (values))
                conn.commit()
                print(i, row['id'], row['name'], row['link'])
                cur.close()
                conn.close()
            except mariadb.Error as error:
                print("Failed to read data from table", error)
            finally:
                if conn:
                    conn.close()
                    print('Connection to db was closed!')
    elif str(imported[0]) == 'user_groups_relation':
        csvData = pd.read_csv(filePath, names=USERS_GROUPS_HEADER, header=None)
        for i, row in csvData.iterrows():
            if row[0] == 'id':
                continue
            sql = "INSERT INTO user_groups_relation (id, user_id, group_id) VALUES (%s, %s, %s)"
            values = [row['id'], row['user_id'], row['group_id']]
            try:
                cur = conn.cursor(buffered = True)
                cur.execute(sql, (values))
                conn.commit()
                print(i, row['id'], row['user_id'], row['group_id'])
                cur.close()
                conn.close()
            except mariadb.Error as error:
                print("Failed to read data from table", error)
            finally:
                if conn:
                    conn.close()
                    print('Connection to db was closed!')
    elif str(imported[0]) == 'group_perm_relation':
        csvData = pd.read_csv(filePath, names=APPS_PERMS_HEADER, header=None)
        for i, row in csvData.iterrows():
            if row[0] == 'id':
                continue
            sql = "INSERT INTO group_perm_relation (id, group_id, perm_id) VALUES (%s, %s, %s)"
            values = [row['id'], row['group_id'], row['perm_id']]
            try:
                cur = conn.cursor(buffered = True)
                cur.execute(sql, (values))
                conn.commit()
                print(i, row['id'], row['group_id'], row['perm_id'])
                cur.close()
                conn.close()
            except mariadb.Error as error:
                print("Failed to read data from table", error)
            finally:
                if conn:
                    conn.close()
                    print('Connection to db was closed!')

#==============================================================================#