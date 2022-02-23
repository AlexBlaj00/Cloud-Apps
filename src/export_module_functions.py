#!/usr/bin/env python3

from global_variables import *
from passlib.hash import sha256_crypt
import mysql.connector as mariadb

#==============================================================================#
###
# Check if a user that tries to login exists in the db based on the username/email 
# provided. If it exists, verify if the passwords match and return a response
###

def check_if_data_is_good(user_login, password):
    query = ""
    response = []

    # select data from db based on what was provided (username or email)
    if check_email(user_login):
        query = "SELECT id, email, password FROM users WHERE email = '" + user_login + "';"
    else:
        query = "SELECT id, username, password FROM users WHERE username = '" + user_login + "';"
    
    # connection to db
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        # position the cursor
        cur = conn.cursor(buffered = True)
        # execute the query and fetch the result
        cur.execute(query)
        user_data = cur.fetchall()

        # if no user that has the specifed username/email was found, then it means
        # that the user doesn't exist and we should return an error
        if not user_data:            
            response.append('ERROR')
            response.append("There is no user defined with these credentials!\n")
        else:
            # else check if the password provided matches the hash stored in the 
            # database and generate a response
            print("DB pass_hash: " + user_data[0][2] + "\n plaintext: " + password)
            if sha256_crypt.verify(password, user_data[0][2]):
                # passwords match
                response.append('OK')
                response.append(user_data[0][0])
            else:
                # passwords do not match
                response.append('ERROR')
                response.append("Incorrect password!\n")

        # close the connection
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if (conn):
            conn.close()
            print('Connection to db was closed!')
    # return the response
    return response

#==============================================================================#
###
# Login user and retrieve list of permissions based on the current app from which 
# the user tries to login and the groups that the user is a part of.
###

def login_user(app_id, user_login, password):
    # verify if the credentials provided are valid or not
    login_response = check_if_data_is_good(user_login, password)
    
    # if there was an error at the verify stage, don't go further and return the error
    if login_response[0] == "ERROR":
        return login_response

    # else get the group ids that the user is a part of
    response = []
    group_query  = ("SELECT group_id FROM user_groups_relation WHERE user_id = "
                    + str(login_response[1]) + ";")

    # connection to db
    conn = mariadb.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, 
        password=DB_PASSWORD, database=DB_DATABASE)
    try:
        # position the cursor
        cur = conn.cursor(buffered = True)
        # execute the query and fetch the result
        cur.execute(group_query)
        group_ids = cur.fetchall()

        # if the user isn't part of any group then it means that he/she has no
        # access to anything and shouldn't be allowed to login here
        if not group_ids:            
            response.append('ERROR')
            response.append("You are not a part of any group and don't have" 
                            " access to anything. CHeck with you IT administrator "
                            "if you think there is a mistake.\n")
        else:
            # else grab all the permissions associated with the groups that
            # the current user is a part of 
            print("Got the group_ids for the user: \n")# + group_ids)
            for g in group_ids:
                print(g)

            perm_query = ("SELECT perm_id FROM groups_perm_relation "
                         "WHERE group_id IN (")
            # generate the list of group ids for the query
            for i in range(0, len(group_ids)):
                if i != len(group_ids) - 1:
                    perm_query += str(group_ids[i][0]) + ", "
                else:
                    perm_query += str(group_ids[i][0]) + "); "

            # execute the query and fetch the result
            cur.execute(perm_query)
            perm_ids = cur.fetchall()

            # if there are no permissions defined for any of the groups there
            # must be an error somewhere. Send that response to the user
            if not perm_ids:
                response.append("ERROR")
                response.append("There are no permissions defined for the " 
                                "groups that you are a part of! Check with your "
                                "IT administator if you think there is a "
                                "mistake.\n")
            else:
                # else filter from all the permissions and get only the ones that
                # correspond to the current app that the user tries to access
                print("Got the perm_ids for the user: \n")# + perm_ids)
                for p in perm_ids:
                    print(p)
            
                perm_query = ("SELECT name FROM permissions WHERE "
                              "app_id = " + str(app_id) + " AND id IN (")
                # generate the list of perm ids for the query
                for i in range(0, len(perm_ids)):
                    if i != len(perm_ids) -1:
                        perm_query += str(perm_ids[i][0]) + ", "
                    else:
                        perm_query += str(perm_ids[i][0]) + ");"

                # execute the query and fetch the result
                cur.execute(perm_query)
                app_perms = cur.fetchall()
                
                # if there are no permissions defined for the current app then it
                # means that the user is not meant to access it 
                if not app_perms:
                    response.append("ERROR")
                    response.append("You have no permissions defined for the " 
                                    "current application! Check with your "
                                    "IT administator if you think there is a "
                                    "mistake.\n")
                else:
                    # else the user has some access to the app
                    # send the list of permissions back to the app to let it
                    # interpret and deliver the accesible data to the user
                    response.append("OK")
                    print("Got the app_perms for the user: \n")# + app_perms)
                    for a in app_perms:
                        print(a)
                    for p in app_perms:
                        response.append(p[0])

        # close the connection
        cur.close()
        conn.close()
    except mariadb.Error as error:
            print("Failed to read data from table", error)
    finally:
        if (conn):
            # if somehow the connection to db was left open, close it
            conn.close()
            print('Connection to db was closed!')
    # return the response
    return response

#==============================================================================#