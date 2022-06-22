import re
class sign_up_pers:
  def __init__(self, full_name, user_name, email, phone, password, pass_confirm):
    self.full_name = full_name
    self.user_name = user_name
    self.email = email
    self.phone = phone
    self.password = password
    self.pass_confirm = pass_confirm

  def check_pass(self, pass_confirm):
    if pass_confirm != self.password:
      return False
    return True

  def insert(self, passwd):
    query = "Insert into users(username,password,full_name,email,phone_number)"\
    "values (\"" + self.user_name + "\", \"" + passwd + "\", \"" + self.full_name + "\", \""\
    + self.email + "\", \"" + self.phone + '\");'
    return query
    
  def check_email(self):
    email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    if email_regex.match(self.email):
      return True
    else:
      return False
  
  
  def select(self):
    query = "Select username from users;"
    return query
    
    
  
