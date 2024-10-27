from flask import current_app as app
from flask import Flask, request
from passlib.hash import pbkdf2_sha256
from jose import jwt
from main import tools
from main import auth
import json


# get a list of all users
# get a list of all users with a specific role
# activate and deactivate a user



class Admin:
    def listOfUsers(self):
        # get the list of all users in the database
        # return a list of users
        # get a specific query from the body 
        data = json.loads(request.data)
        users = app.db.users.find(data, {"_id": 0, "id": 1, "email": 1, "first_name": 1, "last_name": 1, "is_admin": 1, "ip_addresses": 1, "acct_active": 1, "date_created": 1, "last_login": 1})

        responseData = []
        for user in users:
            responseData.append(user)

        

        resp = tools.JsonResp(responseData, 200)
        return resp
    
    #




