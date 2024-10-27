from flask import current_app as app
from flask import Flask, request
from functools import wraps
from main.tools import JsonResp
from jose import jwt
import datetime


# admin decorator
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # get the token from the bearer function
        access_token = request.headers.get('AccessToken')
        
        try:
            token_data = jwt.decode(access_token, app.config['SECRET_KEY'])
        except Exception as e:
            return JsonResp({ "message": "Token is invalid", "exception": str(e) }, 401)

        user = app.db.users.find_one({ "id": token_data['user_id'] }, {
        "_id": 0,
        "password": 0
        })

        
        if "is_admin" in user and user["is_admin"] :
            return f(*args, **kwargs)
        else:
            return JsonResp({ "message": "Admin access required" }, 401)

    return decorated
        


		