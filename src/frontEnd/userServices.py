from email import charset
from urllib import response
from flask import Flask, flash, redirect, render_template, request, session, abort, flash, url_for, request, jsonify
import requests
import json
import pandas as pd

class UserServices:
    @staticmethod
    def user_home(user_id):
        perms_list = []
        url = "http://backend-container:5000/user_home/" + str(user_id)
        response = requests.request("GET", url = url)
        if response:
            perms_list = response.json()
        else:
            return -1
        return perms_list

    @staticmethod
    def user_groups(user_id):
        user_groups = []
        url = "http://backend-container:5000/user_groups/" + str(user_id)
        response = requests.request("GET", url = url)
        if response:
            user_groups = response.json()
        else:
            return -1
        return user_groups
    
    @staticmethod
    def user_settings_run(user_id):
        url = "http://backend-container:5000/user_settings/" + str(user_id)
        response = requests.get(url)
        data = json.loads(response.text)
        print(data)
        response.status_code == 200
        if response:
            return pd.DataFrame(data)
        else:
            return -1

    @staticmethod
    def user_settings_update(user_id, form):
        url = "http://backend-container:5000/user_settings_update/" + str(user_id)
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

