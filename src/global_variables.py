from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort, flash, url_for, make_response
import re
import mysql.connector as mariadb

#==============================================================================#

# the app variable used for app routing
app = Flask(__name__, static_url_path="/static", template_folder="templates")
user_id = []
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER
USERS_HEADER = ['id', 'username', 'password', 'full_name', 'email', 'phone_number', 'is_admin']
GROUPS_HEADER = ['id', 'name', 'description']
PERMS_HEADER = ['id', 'name', 'description', 'app_id']
APPS_HEADER = ['id', 'name', 'link']
USERS_GROUPS_HEADER = ['id', 'user_id', 'group_id']
APPS_PERMS_HEADER = ['id', 'group_id', 'perm_id']

#==============================================================================#

# database login details to freemysql_hosting
DB_HOST = '199.247.4.112'
DB_USER = 'sky_admin'
DB_PASSWORD = 'h^g8p{66TgW'
DB_DATABASE = 'sky_security'
DB_PORT = 3306

#==============================================================================#

# must have function 
def init():
    app = Flask(__name__, static_url_path="/static", template_folder="templates")

#==============================================================================#
###
# set the user_name & user_id variable to a specific value
###
def set_user(id):
    global  user_id
    user_id.insert(0, id)
#    resp = make_response()
#    resp.set_cookie('user_id', str(id))
#    return resp

#==============================================================================#
###
# unset the user_name & user_id
###
def unset_user():
    global user_id
    user_id.pop(0)
#    resp = make_response()
#    resp.set_cookie('user_id', '', expires = 0)
#    return resp

#==============================================================================#
###
# Check if Email has a valid format
###
def check_email(Email):
    email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    if email_regex.match(Email):
      return True
    else:
      return False

#==============================================================================#
###
# Check if phone_number has a valid format
###
def check_phone(phone_number):
    if re.search(r"^(\d{3}\d{3}\d{4})$", phone_number):
        return True
    else:
        return False

#==============================================================================#
###
# Redirect the user to the login page if it's not logged in
###
def is_logged_in():
    # if the user is not logged in, redirect him/her to the login page
    if not session.get('logged_in'):
        return render_template('common_files/login.html')

#==============================================================================#
###
# Verify if a group name is in the list or not
###
def is_group_in_list(admin_groups, group):
    # verify if a specific group name is in the list or not
    for group_row in admin_groups:
        if group == group_row[0]:
            return True
    return False

#==============================================================================#
###
# Create the dictionary that stores if the current user is a part of the group
# or not - dictionary with {name, yes/no} pairs
###
def create_group_dict(group_names, admin_groups):
    groups = {}
    for group_row in group_names:
        if is_group_in_list(admin_groups, group_row[0]):
            groups[ group_row[0] ] = "Yes"
        else:
            groups[ group_row[0] ] = "No"
    return groups

#==============================================================================#
###
# Creates a string with the specified ids in the form of (1, 2, 3);
###
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
###
# Check if a user is an admin and update it in the db 
###

def is_user_admin():
    queries = []
    queries.append("SELECT is_admin FROM users WHERE id = " + str(user_id[0]))

    print(queries[0] + "------------------------")

    # connection to the db
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
      cur = conn.cursor(buffered = True)
      cur.execute(queries[0])
      is_admin_in_db = cur.fetchall()

      is_admin = is_admin_in_db[0][0]
    
      if(is_admin_in_db[0] == 0):
        queries.append("SELECT g.id FROM groups g"
            "INNER JOIN user_groups_relation ug ON ug.group_id = g.id"
            "WHERE ug.user_id = " + str(user_id[0]))
        cur.execute(queries[1])
        group_ids = cur.fetchall()

        is_in_admin_group = 0
        for id in group_ids:
            if id[0] == 1:
                is_in_admin_group = 1
                break

        if is_in_admin_group & (not is_admin_in_db):
            queries.append("UPDATE users SET is_admin = 1 WHERE id = " 
                + str(user_id[0]))
            cur.execute(queries[2])
            conn.commit()
            is_admin = 1

      # close the connection
      cur.close()
      conn.close()
    except mariadb.Error as error:
        print("Failed to read data from table", error)
    finally:
      if conn:
        conn.close()
        print('Connection to db was closed!')
    
    return is_admin

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