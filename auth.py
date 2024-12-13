from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from db.models import *
from functools import wraps
import jwt
from flask import request, abort
from flask import current_app
import requests

User_db = Userdb()



def authenticate_user(email, pwd):
    user_profile = User_db.get_user_by_email(email)
    
    if user_profile: 
        authenticated = check_password_hash(user_profile["password"], pwd)
        if authenticated and user_profile["active"]:
            return user_profile
        else:
            return False
    else:
        return "not found"
    



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            print(token)
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user=User_db.get_user_by_id(data["user_id"])
            if current_user is None:
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
            
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500
        current_user["_id"] = str(current_user["_id"])
        del current_user["password"]
        
        return f(current_user, *args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            print(token)
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user=User_db.get_user_by_id(data["user_id"])
            if current_user is None:
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
                
            if current_user["role"]!= "Admin":
                return {
                "message": "You do not have permission to access this resource!",
                "data": None,
                "error": "Unauthorized"
            }, 401
            
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs)

    return decorated

def master_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            print(token)
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user=User_db.get_user_by_id(data["user_id"])
            if current_user is None:
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
                
            if current_user["role"]!= "waste-master":
                return {
                "message": "You do not have permission to access this resource!",
                "data": None,
                "error": "Unauthorized"
            }, 401
            
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs)

    return decorated


def fs_master_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            print(token)
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
            
        try:
            data=jwt.decode(token, options={"verify_signature": False})
            url = 'https://app.foodsoldiers.io/api/v1/user-detail' 

            headers = {
                'Authorization': f'Bearer {token}'
            }

            response = requests.get(url, headers=headers)

            data = response.json()["data"]
            data["token"] = token  
          
            if data is None:
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
    
            if data["role"] != "waste-master":
                return {
                "message": "You do not have permission to access this resource!",
                "data": None,
                "error": "Unauthorized"
            }, 401
            
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(data, *args, **kwargs)

    return decorated



def fs_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            print(token)
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
            
        try:
            data=jwt.decode(token, options={"verify_signature": False})
            url = 'https://app.foodsoldiers.io/api/v1/user-detail' 

            headers = {
                'Authorization': f'Bearer {token}'
            }

            response = requests.get(url, headers=headers)

            data = response.json()["data"]
            data["token"] = token  
          
            if data is None:
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
    
            if data["role"] != "Admin":
                return {
                "message": "You do not have permission to access this resource!",
                "data": None,
                "error": "Unauthorized"
            }, 401
            
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(data, *args, **kwargs)

    return decorated

def fs_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            print(token)
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            data=jwt.decode(token, options={"verify_signature": False})
            url = 'https://app.foodsoldiers.io/api/v1/user-detail' 

            headers = {
                'Authorization': f'Bearer {token}'
            }

            response = requests.get(url, headers=headers)

            details = response.json()["data"]
            details["token"] = token  
          
            if details is None:
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
            
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(details, *args, **kwargs)

    return decorated

