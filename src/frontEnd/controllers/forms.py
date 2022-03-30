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