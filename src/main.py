from flask import Flask, jsonify
import requests
from flask import Flask, flash, redirect, render_template, request, session, abort, flash, url_for, request
from passlib.hash import sha256_crypt
import mysql.connector as mariadb
import os
import operator
import re
from sign_up import sign_up_pers
from global_variables import *
import admin, user
import numpy as np
import plotly
import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.offline import init_notebook_mode
from OpenSSL import SSL
import ssl
#ssl.PROTOCOL_TLSv1_2
#context = SSL.Context(ssl.PROTOCOL_TLSv1_2)
#context.use_privatekey_file('server.key')
#context.use_certificate_file('server.crt')   
#==============================================================================#

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
    print(query)
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
      print(sql)
  
  # trimitere mail cu parola reseta temporar
  # 
  conn.close()
  cur.close()
  return redirect("/reset")

@app.route('/', methods=['GET'])
def serve():
    return "Hello world", 200

if __name__ == "__main__":
  app.secret_key = os.urandom(12)
  #context = ('cert.perm', 'key.perm')
  app.run(debug=True, host='0.0.0.0', port=5000)


#==============================================================================#
