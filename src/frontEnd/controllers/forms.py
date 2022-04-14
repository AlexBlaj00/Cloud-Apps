from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, IntegerField



class SettingsUpdate(FlaskForm):
    full_name =  HiddenField('full_name' )
    username =  HiddenField('username')
    phone_number =  HiddenField('phone_number')
    password =  HiddenField('password')
    new_password = HiddenField('new_password')
    email =  HiddenField('email')

class AddUser(FlaskForm):
    first_name = HiddenField('first_name')
    last_name = HiddenField('last_name')
    email = HiddenField('email')
    phone_number = HiddenField('phone_number')
    password = HiddenField('password')
    confirm_password = HiddenField('confirm_password')
    username = HiddenField('username')


class AddGroup(FlaskForm):
    id = HiddenField('id')
    name = HiddenField('name')
    description = HiddenField('description')

class AddPermissions(FlaskForm):
    id = HiddenField('id')
    name = HiddenField('name')
    description = HiddenField('description')

class AddApplication(FlaskForm):
    id = HiddenField('id')
    name = HiddenField('name') 
    link = HiddenField('link')

class ModifyGroup(FlaskForm):
    #groups
    id = HiddenField('id')
    name = HiddenField('name')
    description = HiddenField('description')
class ModifyPerms(FlaskForm):    
    #perms
    id_perm = HiddenField('id_perm')
    name_perm = HiddenField('name_perm')
    desc_perm = HiddenField('desc_perm')
    app = HiddenField('app')
class ModifyApp(FlaskForm):    
    #app
    id_app = HiddenField('id_app')
    name_app = HiddenField('name_app')
    link = HiddenField('link')
class ModifyUserGroup(FlaskForm):    
    #usr-group
    id_user = HiddenField('id_user')
    add_group = HiddenField('add_group')
    remove_group = HiddenField('remove_group')
class ModifyGroupPerms(FlaskForm):
    #group-perms
    id_group = HiddenField('id_group')
    add_perm = HiddenField('add_perm')
    remove_perm = HiddenField('remove_perm')
