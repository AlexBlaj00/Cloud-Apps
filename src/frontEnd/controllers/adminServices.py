from urllib import response
from flask import Flask, flash, redirect, render_template, request, session, abort, flash, url_for, request, jsonify
import requests


class AdminServices:
    @staticmethod
    def admin_groups(user_id):
        admin_groups = []
        url = "http://localhost:49156/admin_groups/" + str(user_id)
        response = requests.request("GET", url = url)
        print("In the adminServices_admin_groups")
        print(str(response.text))
        if response:
            admin_groups = response.json()
        else:
            return -1

        return admin_groups

    @staticmethod
    def admin_home(user_id):
        perms_list = []
        url = "http://localhost:49156/admin_home/" +str(user_id)
        response = requests.request("GET", url = url)
        if response:
            perms_list = response.json()
        else:
            return -1

        return perms_list

