from crypt import methods
import imp
from telnetlib import STATUS
from tokenize import group
import requests
from flask import Flask, flash, redirect, render_template, request, session, abort, flash, url_for, request, jsonify
from passlib.hash import sha256_crypt
import mysql.connector as mariadb
import os
import operator
import re
from sign_up import sign_up_pers
from global_variables import *
import numpy as np
import plotly
import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.offline import init_notebook_mode
from OpenSSL import SSL
import ssl
from adminServices import AdminServices
from userServices import UserServices
import re
import string
import json
import forms

#ssl.PROTOCOL_TLSv1_2
#context = SSL.Context(ssl.PROTOCOL_TLSv1_2)
#context.use_privatekey_file('server.key')
#context.use_certificate_file('server.crt')   
#==============================================================================#

#@app.route('/', methods=['POST', 'GET'])
#def smth():
#    res = requests.get("http://localhost:49153/admin_home")
#    return str(res.text)


@app.route('/')
def home():
  if not session.get('logged_in'):
    return render_template("common_files/login.html")
  else:
    is_admin = is_user_admin()
    if is_admin:
      return redirect('/admin_home')
    else:
      return redirect('/user_home')

#==============================================================================#

@app.route('/login', methods=['POST','GET']) 
def do_admin_login():
  login = request.form

  # if the sign up button was pressed
  if login.get('sign_up'):
    return redirect("/sign_up")

  query = ("SELECT a.name, p.name, g.name, gpr.perm_id FROM "
           "groups_perm_relation AS gpr INNER JOIN groups AS g "
           "ON g.id = gpr.group_id INNER JOIN permissions AS p "
           "ON gpr.perm_id = p.id INNER JOIN apps AS a ON p.app_id = a.id "
           "WHERE perm_id IN (  SELECT id FROM permissions WHERE app_id = 3) "
           "ORDER BY p.name;")
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


  password = str(login.get("password", False))
  email = str(login.get("email-username", False))
  username = str(login.get("email-username", False))

  check = 0
  conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
  try:
    
    cur = conn.cursor(buffered = True)
    if check_email(email):
      data = cur.execute("SELECT id, username, email, password FROM users WHERE email= %s ", (email,))  #check dupa username sau email
    else:
      data = cur.execute("SELECT id, username, email, password FROM users WHERE username= %s ", (username,))

    data = cur.fetchall() 

    # close the connection
    cur.close()
    conn.close()
  except mariadb.Error as error:
        print("Failed to read data from table", error)
  finally:
    if (conn):
      conn.close()
      print('Connection to db was closed!')

  # if there is no data from db aka there is no user stored in db with that
  # username or email  
  if not data:
    error = 'Invalid credentials!'
    flash(error)
    return redirect("/")

  # check the username/email if it matches with the one stored
  for i in data[:][0]:
    if i == email or i == username:
      check += 1
  
  # verify if the hash matches the string from the form 
  if sha256_crypt.verify(password, data[0][3]):
    check += 1

  if check != 2:
    error = 'Wrong password or email!'
    flash(error)
    return redirect("/")

  # if it reaches this code than it means that all the login details are 
  # correct
  session['logged_in'] = True
    
  # save the username in a global variable so that you can access it from other scripts
  set_user(data[0][0])
  # return the appropriate page
  return home()

#==============================================================================#
@app.route('/admin_groups')
def admin_groups_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()
    groups = AdminServices.admin_groups(user_id[0])
    #for key, value in groups.items():
    #    print(key + "-------" + value)
    return render_template('admin_files/admin_groups.html', groups = groups
        )
#==============================================================================#
@app.route('/admin_home')
def admin_home_run():
   # if the user is not logged in, redirect him/her to the login page
    is_logged_in()
    app_perms_list = AdminServices.admin_home(user_id[0])
    # return the page with all the data stored in the app_perms_list variable
    return render_template('admin_files/admin_home.html', app_perms_list = app_perms_list)
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
@app.route("/admin_settings", methods = ['POST', 'GET'])
def admin_settings_run():
  is_logged_in()
  users_final = []
  users = AdminServices.admin_settings_run(user_id[0])

  for index, row in users.iterrows():
    users_final.append(row[0])
    
  form = forms.SettingsUpdate(request.form)
  users_dict = {0: users_final[1], 1: users_final[3], 2: users_final[4], 3: users_final[5]}
  return render_template("admin_files/admin_settings.html", users = users_dict, STATUS = 200, form = form)

#==============================================================================#
@app.route("/admin_settings_update", methods = ['POST'])
def admin_settings_update():
  is_logged_in()
  form = forms.SettingsUpdate(request.form)
  req = AdminServices.admin_settings_update(user_id[0], form)
  return admin_settings_run()
#==============================================================================#
@app.route('/delete_user', methods = ['GET', 'POST'])
def delete_user_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()
    users = AdminServices.delete_user_run() 
    return render_template('admin_files/admin_delete_user.html', users = users.json())
#==============================================================================#
@app.route('/delete_user_exec', methods=['POST'])
def execute_delete_user():
    # get the list of ids that the admin wants to delete
    delete = request.form.getlist('checks')
    service = AdminServices.execute_delete_user(delete)
    if (service.status_code == 200):
      flash("Succesfully deleted selected users!")
    else:
      flash("Something went wrong, try again.")
    return redirect("/delete_user")
#==============================================================================#
@app.route('/delete_group', methods = ['GET'])
def delete_group_run():
     is_logged_in()
     groups = AdminServices.delete_group_run()
     return render_template('admin_files/admin_delete_group.html', groups = groups.json())
#==============================================================================#
@app.route('/delete_group_exec', methods = ['POST'])
def execute_delete_group():
  delete = request.form.getlist('checks')
  service = AdminServices.execute_delete_group(delete)
  return redirect('/delete_group')
#==============================================================================#
@app.route('/delete_perm')
def delete_perm_run():
    is_logged_in()
    perms = AdminServices.delete_perm_run()
    return render_template('admin_files/admin_delete_perm.html', perms = perms.json())
#==============================================================================#
@app.route('/delete_perm_exec', methods = ['POST'])
def execute_delete_perm():
    delete = request.form.getlist('checks')
    service = AdminServices.execute_delete_perm(delete)
    return redirect('/delete_perm')
#==============================================================================#
@app.route('/delete_app')
def delete_app_run():
    is_logged_in()
    apps = AdminServices.delete_app_run()
    return render_template('admin_files/admin_delete_app.html', apps = apps.json())
#==============================================================================#
@app.route('/delete_app_exec', methods = ['POST'])
def execute_delete_app():
  delete = request.form.getlist('checks')
  service = AdminServices.execute_delete_app(delete)
  return redirect('/delete_app')
#==============================================================================#
@app.route('/add_user')
def admin_add_user():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()
    groups = AdminServices.admin_add_user()
    return render_template('admin_files/admin_add_user.html', groups = groups.json())  
#==============================================================================#
@app.route('/add_group', methods=['POST','GET'])
def admin_add_group():
    is_logged_in()
    groups = AdminServices.getGroups()
    users = AdminServices.getUser()
    permissions = AdminServices.getPerms()
    
    return render_template('admin_files/admin_add_group.html', groups = groups, users = users, permissions = permissions)
#==============================================================================#
@app.route('/add_group_run', methods = ['POST'])
def insert_groups():
    form = forms.AddGroup(request.form)
    users = request.form.getlist('users')
    perms = request.form.getlist('permissions')
    services = AdminServices.insert_groups(form, users, perms)
    
    return redirect('/add_group')
#==============================================================================#
@app.route('/submit_user', methods = ['GET', 'POST'])
def submit_user_form():
    groups = request.form.getlist('groups')
    form = forms.AddUser(request.form)
    service = AdminServices.submit_user_form(form, groups)
    if (service.status_code == 200):
       flash("Succesfully created user!")
    else:
        flash("Something went wrong, double check if password correspond, email and phone number as well!")
    return redirect('/add_user')
#==============================================================================#
@app.route('/add_perms', methods = ['GET', 'POST'])
def admin_add_perms():
    perms = AdminServices.getAllPerms()
    groups = AdminServices.getGroups()
    apps = AdminServices.getAllApps()
    return render_template('admin_files/admin_add_perm.html', perms = perms, 
                            groups = groups, apps = apps)  
#==============================================================================#
@app.route('/add_perms_run', methods = ['GET', 'POST'])
def insert_perms():
  id_groups = request.form.getlist('groups')
  id_apps = request.form.getlist('apps')
  form = forms.AddPermissions(request.form)
  service = AdminServices.insert_perms(form, id_apps, id_groups)

  return redirect('/add_perms')
#==============================================================================#
@app.route('/add_apps')
def add_apps_load():
  apps = AdminServices.getApps()
  return render_template('admin_files/admin_add_app.html', apps = apps)
#==============================================================================#
@app.route('/add_apps_run', methods = ['POST'])
def insert_apps(): 
    form = forms.AddApplication(request.form)
    service = AdminServices.insert_apps(form)
    return redirect('/add_apps')
#==============================================================================#
@app.route('/admin_modify', methods = ['POST', 'GET'])
def admin_modify_run():
    is_logged_in()    
    groups = AdminServices.getGroupsMod(user_id[0])
    perms = AdminServices.getPermsMod(user_id[0])
    users = AdminServices.getUser()
    apps = AdminServices.getApps()
    
    return render_template('admin_files/admin_modify.html', groups = groups.json(), perm = perms.json(),  users = users, apps = apps)    

#==============================================================================#
@app.route('/admin_modify_run', methods = ['POST', 'GET'])
def admin_modify_exec():

    form_group = forms.ModifyGroup(request.form)
    form_perms = forms.ModifyPerms(request.form)
    form_app = forms.ModifyApp(request.form)
    form_usrGroup = forms.ModifyUserGroup(request.form)
    form_groupPerms = forms.ModifyGroupPerms(request.form)

    if (form_group.id.data != ""):
      service = AdminServices.admin_modify_group(form_group)
    if (form_perms.id_perm.data != ""):
      service = AdminServices.admin_modify_perm(form_perms)
    if (form_app.id_app.data != ""):
      service = AdminServices.admin_modify_app(form_app)
    if (form_usrGroup.id_user.data != ""):
      service = AdminServices.admin_modify_usrGroup(form_usrGroup)
    if (form_groupPerms.id_group.data != ""):
      service = AdminServices.admin_modify_groupPerms(form_groupPerms)

    return redirect('/admin_modify')
#==============================================================================#
@app.route('/admin_add')
def admin_add_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

    return render_template('admin_files/admin_add_user.html')   
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
@app.route('/admin_contact')
def admin_contact_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()
    
    return render_template('admin_files/admin_contact.html')
#==============================================================================#
@app.route('/user_home')
def user_home_run():
  # if the user is not logged in, redirect him/her to the login page
  is_logged_in()
  app_perms_list = UserServices.user_home(user_id[0])
  return render_template('user_files/user_home.html', app_perms_list = app_perms_list)
#==============================================================================#
@app.route('/user_groups')
def user_groups_run():
  # if the user is not logged in, redirect him/her to the login page
  is_logged_in()
  groups = UserServices.user_groups(user_id[0])
  return render_template('user_files/user_groups.html', groups = groups)
#==============================================================================#
@app.route('/user_msg')
def user_msg_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

    return render_template('user_files/user_msg.html')
#==============================================================================#
@app.route('/user_forum')
def user_forum_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

    return render_template('user_files/user_forum.html')
#==============================================================================#
@app.route('/user_settings', methods =['POST','GET'])
def user_settings_run():

  is_logged_in()
  users_final = []
  users = UserServices.user_settings_run(user_id[0])

  for index, row in users.iterrows():
    users_final.append(row[0])

  form = forms.SettingsUpdate(request.form)
  users_dict = {0: users_final[1], 1: users_final[3], 2: users_final[4], 3: users_final[5]}

  return render_template('user_files/user_settings.html', users = users_dict, STATUS = 200, form = form )
#==============================================================================#
@app.route('/user_settings_update', methods = ['POST'])
def user_settings_update():
  is_logged_in()

  form = forms.SettingsUpdate(request.form)
  req = UserServices.user_settings_update(user_id[0], form)
  return user_settings_run()
#==============================================================================#
@app.route('/user_contact')
def user_contact_run():
    # if the user is not logged in, redirect him/her to the login page
    is_logged_in()

    return render_template('user_files/user_contact.html')
#==============================================================================#

#==============================================================================#
@app.route('/sign_up')
def sign_up():
  return render_template("common_files/sign_up.html")

#==============================================================================#

@app.route('/login_button')
def login_button():
  return redirect('/')

#==============================================================================#

@app.route('/sign_up_run', methods=['POST', 'GET']) 
def do_admin_sign_up():
  request_sign = request.form

  # if the sign up button was pressed
  if request_sign.get('login'):
    return redirect("/")

  full_name = str(request_sign.get('full_name', False))
  user_name = str(request_sign.get('user_name', False))
  email = str(request_sign.get('email', False))
  phone = str(request_sign.get('phone', False))
  password = str(request_sign.get('password', False))
  pass_conf = str(request_sign.get('confirm_password', False))
  
  sign_up_pers1 = sign_up_pers(full_name, user_name, email, phone, password, pass_conf)
  
  conn = mariadb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
       database=DB_DATABASE)
  try:
    cur = conn.cursor(buffered=True)
    cur.execute(sign_up_pers1.select())
    users_rows = cur.fetchall()
    for row in users_rows:
        if user_name == row[0]:
          flash('Invalid User Name.')
          return redirect("/sign_up")

    if not (sign_up_pers1.check_pass(pass_conf) and sign_up_pers1.check_email()):
      flash('Please check your sign up details and try again.')
      return redirect("/sign_up")

    pass_hash = sha256_crypt.hash(password)
    
    cur.execute(sign_up_pers1.insert(pass_hash))
    conn.commit()
    cur.close()
    conn.close()
  except mariadb.Error as error:
        print("Failed to read data from table", error)
  finally:
    if conn:
      conn.close()
      print('Connection to db was closed!')

  return redirect("/")

#==============================================================================#

@app.route('/logout')
def logout():
  session['logged_in'] = False
  unset_user()
  return redirect("/")

#==============================================================================#

@app.route('/reset')
def reset():
  return render_template('common_files/reset.html')

#==============================================================================#

@app.route('/reset_password', methods = ['POST','GET'])
def reset_password():
  conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
  cur = conn.cursor(buffered=True)
  if request.method == 'POST':
    if request.form.get('email'):
      email = request.form.get('email')
      sql = "SELECT id from users WHERE email = " + "'" + email + "'"
      cur.execute(sql)
      sql = cur.fetchone()[0]
  
  conn.close()
  cur.close()
  return redirect("/reset")

@app.route('/', methods=['GET'])
def serve():
    return "Hello world", 200

if __name__ == "__main__":
  app.secret_key = os.urandom(12)
  #context = ('cert.perm', 'key.perm')
  app.run(debug=True, host='0.0.0.0', port=5001)


#==============================================================================#
