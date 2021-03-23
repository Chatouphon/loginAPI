from typing import Optional

from fastapi import FastAPI
import connection
from bson import ObjectId
from json import dumps
from schematics.models import Model
from schematics.types import StringType, EmailType

class User(Model):
    user_id = ObjectId()
    email = EmailType(required=True)
    name = StringType(required=True)
    password = StringType(required=True)

# An instance of class User
newuser = User()

# function to create and assign values to the instance of class User created
def create_user(email, username, password):
    newuser.user_id = ObjectId()
    newuser.email = email
    newuser.name = username
    newuser.password = password
    return dict(newuser)

# A method to check if the email parameter exists from the users database before validation of details
def email_exists(email):
    user_exists = True

    # counts the number of time the email exists, if it equals 0 it means the email doesn't exist in the database
    if connection.db.users.find(
        {'email': email}
    ).count() == 0:
        user_exists = False
        return user_exists

# Reads user details from database and ready for validation
def check_login_creds(email, password):
    if not email_exists(email):
        activeuser = connection.db.users.find(
            {'email': email}
        )
        for actuser in activeuser:
            actuser = dict(actuser)
            # Converted the user ObjectId to str! so this can be stored into a session(how login works)
            actuser['_id'] = str(actuser['_id'])
            return actuser

app = FastAPI()

# root endpoint
@app.get("/")
def index():
    return {"message": "Hello dear"}

# Signup endpoint with the POST method
@app.post("/signup/{email}/{username}/{password}")
def signup(email, username: str, password: str):
    user_exists = False
    data = create_user(email, username, password)

    # Convert data to dict so it can be easily inserted to MongoDB
    dict(data)

    # Checks if an email exists from the collection of users
    if connection.db.users.find(
        {'email': data['email']}
        ).count() > 0:
        user_exists = True
        print("User Exists")
        return {"message":"User Exists"}
    # If the email doesn't exist, create the user
    elif user_exists == False:
        connection.db.users.insert_one(data)
        return {"message":"User Created", "email": data['email'], "name": data['name'], "pass": data['password']}

# Login endpoint
@app.get("/login/{email}/{password}")
def login(email, password):
    def log_user_in(creds):
        if creds['email'] == email and creds['password'] == password:
            return {"message": creds['name'] + ' successfully logged in'}
        else:
            return {"message":"Invalid credentials!!"}
    # Read email from database to validate if user exists and checks if password matches
    logger = check_login_creds(email, password)
    if bool(logger) != True:
        if logger == None:
            logger = "Invalid Email"
            return {"message":logger}
    else:
        status = log_user_in(logger)
        return {"Info":status}

# Edit endpoint
@app.put("/edit/{email}")
def edit_user(email, name: Optional[str] = None, password: Optional[str] = None):
    user_exists = False
    data = create_user(email, name, password)
    dict(data)
    current_user = connection.db.users.find({'email': data['email']})
    # if name == None:
    #     name = current_user._name
    #     data = create_user(email, name, password)
    #     dict(data)
    if current_user.count() > 0:
        user_exists = True
        print("User Exists")
        connection.db.users.find_one_and_update(
            {'email': data['email']}, {'$inc': {'count': 1},'$set': {'name': name, 'password': password}}
        )
        return {"message":"Updated"}
    elif user_exists == False:
        return {"user not update"}

# Delete endpoint

