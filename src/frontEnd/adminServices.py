from email import charset, header
import re
from urllib import response
from flask import Flask, flash, redirect, render_template, request, session, abort, flash, url_for, request, jsonify
import requests
import json
import pandas as pd
from global_variables import *
from werkzeug.routing import BaseConverter

class IntListConverter(BaseConverter):
    regex = r'\d+(?:,\d+)*,?'

    def to_python(self, value):
        return [int(x) for x in value.split(',')]

    def to_url(self, value):
        return ','.join(str(x) for x in value)

app.url_map.converters['int_list'] = IntListConverter

class AdminServices:
    @staticmethod
    def admin_groups(user_id):
        admin_groups = []
        url = "http://backend-container:5000/admin_groups/" + str(user_id)
        response = requests.request("GET", url = url)
        if response:
            admin_groups = response.json()
        else:
            return -1

        return admin_groups

    @staticmethod
    def admin_home(user_id):
        perms_list = []
        url = "http://backend-container:5000/admin_home/" +str(user_id)
        response = requests.request("GET", url = url)
        if response:
            perms_list = response.json()
        else:
            return -1

        return perms_list

    @staticmethod
    def admin_settings_run(user_id):
        url = "http://backend-container:5000/admin_settings/" + str(user_id)
        response = requests.get(url)
        data = json.loads(response.text)
        response.status_code == 200
        if response:
            return pd.DataFrame(data)
        else:
            return -1

    @staticmethod
    def admin_settings_update(user_id, form):
        url = "http://backend-container:5000/admin_settings_update/" + str(user_id)
        headers = {
            'Content-Type' : 'application/json'
        }

        payload = {
            "full_name" : form.full_name.data,
            "username" : form.username.data,
            "phone_number" : form.phone_number.data,
            "email" : form.email.data,
            "password" : form.password.data,
            "new_password" : form.new_password.data
        }

        payload = json.dumps(payload)
        response = requests.post(url = url, data = payload, headers = headers)
        return response

    @staticmethod
    def delete_user_run():
        url = "http://backend-container:5000/delete_user"
        response = requests.request('GET', url= url)
        
        response.status_code == 200
        if response:
            return response
        else:
            return -1
    
    @staticmethod
    def execute_delete_user(delete):
        url = "http://backend-container:5000/delete_user_exec/" 
        for i in delete:
            url += str(i) + ","
        url = url[:-1]
       
        response = requests.request('POST', url= url)
        
        if response:
            response.status_code == 200
            return response
        else:
            return -1
    @staticmethod
    def admin_add_user():
        url = "http://backend-container:5000/add_user"
        response = requests.request('GET', url = url)
        if response:
            response.status_code == 200
            return response
        else:
            return -1
    
    @staticmethod
    def submit_user_form(form, groups):
        url = "http://backend-container:5000/submit_user/"
        for i in groups:
            url += str(i) + ","
        url = url[:-1]
        headers = {
            'Content-Type' : 'application/json'
        }

        payload = {
            "first_name" : form.first_name.data,
            "last_name" : form.last_name.data,
            "email" : form.email.data,
            "phone_number" : form.phone_number.data,
            "password" : form.password.data,
            "confirm_password" : form.confirm_password.data,
            "username" : form.username.data
        }

        payload = json.dumps(payload)
        response = requests.post(url = url, data = payload, headers = headers)
        return response

    @staticmethod
    def getUser():
        url_users = "http://backend-container:5000/getUsers"
        users = requests.request('GET', url = url_users)
        if users:
            users.status_code == 200
            return users.json()
        else:
            return -1
    
    @staticmethod
    def getGroups():
        url_groups = "http://backend-container:5000/getGroup"
        groups = requests.request('GET', url = url_groups)
        if groups:
            groups.status_code == 200
            return groups.json()
        else:
            return -1

    @staticmethod
    def getPerms():
        url_permissions = "http://backend-container:5000/getPermissions"
        permissions = requests.request('GET', url = url_permissions)
        if permissions:
            permissions.status_code == 200
            return permissions.json()
        else:
            return -1

    @staticmethod
    def getAllPerms():
        url_permissions = "http://backend-container:5000/getAllPermissions"
        permissions = requests.request('GET', url = url_permissions)
        if permissions:
            permissions.status_code == 200
            return permissions.json()
        else:
            return -1

    @staticmethod
    def getAllApps():
        url = "http://backend-container:5000/getApps"
        apps = requests.request('GET', url = url)
        if apps:
            apps.status_code == 200
            return apps.json()
        else:
            return -1

    @staticmethod
    def getApps():
        url = "http://backend-container:5000/getAllApps"
        apps = requests.request('GET', url = url)
        if apps:
            apps.status_code == 200
            return apps.json()
        else:
            return -1                                

    @staticmethod
    def insert_groups(form, users, permission):
        url = "http://backend-container:5000/add_group_run/"
        for i in users:
            url += str(i) + ","
        url = url[:-1]
        url += "/"
        for i in permission:
            url += str(i) + ","
        url = url[:-1]
       
        headers = {
            'Content-Type' : 'application/json'
        }

        payload = {
            "name" : form.name.data,
            "description" : form.description.data
        }
        
        payload = json.dumps(payload)
        response = requests.post(url = url, data = payload, headers = headers)
        return True        


    @staticmethod
    def insert_perms(form, perms, groups):
        url = "http://backend-container:5000/add_perms_run/"
        for i in groups:
            url += str(i) + ","
        url = url[:-1]
        url += "/"
        for i in perms:
            url += str(i) + ","
        url = url[:-1]

        headers = {
            'Content-Type' : 'application/json'
        }

        payload = {
            "name" : form.name.data,
            "description" : form.description.data
        }

        payload = json.dumps(payload)
        response = requests.post(url = url, data = payload, headers = headers)
        return True

    @staticmethod
    def insert_apps(form):
        url = "http://backend-container:5000/add_apps_run"

        headers = {
            'Content-Type' : 'application/json'
        }

        payload = {
            "name" : form.name.data,
            "link" : form.link.data
        }

        payload = json.dumps(payload)
        response = requests.post(url = url, data = payload, headers = headers)
        return True


    @staticmethod
    def delete_group_run():
        url = "http://backend-container:5000/delete_group"

        response = requests.request('GET', url = url)
        if response:
            response.status_code == 200
            return response
        else:
            return -1
    @staticmethod
    def execute_delete_group(delete):
        url = "http://backend-container:5000/delete_group_exec/"
        for i in delete:
            url += str(i) + ","
        url = url[:-1]
        response = requests.request('POST', url = url)
        if response:
            response.status_code == 200
            return response
        else:
            return -1

    @staticmethod
    def delete_perm_run():
        url = "http://backend-container:5000/delete_perm"
        response = requests.request('GET', url = url)
        if response:
            response.status_code == 200
            return response
        else:
            return -1        

    @staticmethod
    def execute_delete_perm(delete):
        url = "http://backend-container:5000/delete_perm_exec/"
        for i in delete:
            url += str(i) + ","
        url = url[:-1]
        response = requests.request('POST', url = url)
        if response:
            response.status_code == 200
            return response
        else:
            return -1

    @staticmethod
    def delete_app_run():
        url = "http://backend-container:5000/delete_app"
        response = requests.request('GET', url = url)
        if response:
            response.status_code == 200
            return response
        else:
            return -1

    @staticmethod
    def execute_delete_app(delete):
        url = "http://backend-container:5000/delete_app_exec/"
        for i in delete:
            url += str(i) + ","

        url = url[:-1]
        response = requests.request('POST', url = url)
        if response:
            response.status_code == 200
            return response
        else:
            return -1       

    @staticmethod
    def getGroupsMod(user_id):
        url = "http://backend-container:5000/admin_group_modify/" + str(user_id)
        response = requests.get(url)
        if response:
            response.status_code == 200
            return response
        else:
            return -1

    @staticmethod
    def getPermsMod(user_id):
        url = "http://backend-container:5000/admin_perms_modify/" + str(user_id)
        response = requests.get(url)
        if response:
            response.status_code == 200
            return response
        else:
            return -1         

    @staticmethod
    def admin_modify_group(form):
        url = "http://backend-container:5000/admin_modify"
        headers = {
            'Content-Type' : 'application/json'
        }

        if form.id.data != None:
            payload = {
                "id" : form.id.data,
                "name" : form.name.data,
                "description" : form.description.data
            }
            payload = json.dumps(payload)
            response = requests.post(url = url, data = payload, headers = headers)
            return True
    @staticmethod
    def admin_modify_perm(form):        
        url = "http://backend-container:5000/admin_modify"
        headers = {
            'Content-Type' : 'application/json'
        }

        if form.id_perm.data != None:
            payload = {
                "id_perm" : form.id_perm.data,
                "name_perm" : form.name_perm.data,
                "desc_perm" : form.desc_perm.data,
                "app" : form.app.data
            }
        payload = json.dumps(payload)
        response = requests.post(url = url, data = payload, headers = headers)
        return True
    @staticmethod
    def admin_modify_app(form):

        url = "http://backend-container:5000/admin_modify"
        headers = {
            'Content-Type' : 'application/json'
        }   

        if form.id_app.data != None:
            payload = {
                "id_app" : form.id_app.data,
                "name_app" : form.name_app.data,
                "link" : form.link.data
            }
        payload = json.dumps(payload)
        response = requests.post(url = url, data = payload, headers = headers)
        return True    
    @staticmethod
    def admin_modify_usrGroup(form):
        url = "http://backend-container:5000/admin_modify"
        headers = {
            'Content-Type' : 'application/json'
        }

        if form.id_user.data != None:
            payload = {
                "id_user" : form.id_user.data,
                "add_group" : form.add_group.data,
                "remove_group" : form.remove_group.data
            }
        payload = json.dumps(payload)
        response = requests.post(url = url, data = payload, headers = headers)
        return True   

    @staticmethod
    def admin_modify_groupPerms(form):

        url = "http://backend-container:5000/admin_modify"
        headers = {
            'Content-Type' : 'application/json'
        }    

        if form.id_group.data != None:
            payload = {
                "id_group" : form.id_group.data,
                "add_perm" : form.add_perm.data,
                "remove_perm" : form.remove_perm.data
            }
        payload = json.dumps(payload)
        response = requests.post(url = url, data = payload, headers = headers)
        return True 

    @staticmethod
    def do_dashboard1():
        url = "http://reporting-container:5003/admin_dashboard1"
        response = requests.get(url)
        if response:
            response.status_code == 200
            return response
        else:
            return -1

    @staticmethod
    def do_dashboard2():
        url = "http://reporting-container:5003/admin_dashboard2"
        response = requests.get(url)
        if response:
            response.status_code == 200
            return response
        else:
            return -1 

    @staticmethod
    def do_dashboard3():
        url = "http://reporting-container:5003/admin_dashboard3"
        response = requests.get(url)
        if response:
            response.status_code == 200
            return response
        else:
            return -1                        