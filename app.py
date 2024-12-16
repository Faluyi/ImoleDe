from flask import Flask, request, jsonify, session
from flask_mail import Mail, Message
from db.models import Usersdb, OTPdb, SolarInvertersdb, Devicesdb, DistributionBoardAndSmartSwitchesdb
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from flask_cors import CORS
from auth import authenticate_user, token_required, admin_required
import jwt 
import pyotp
from properties import *
from pymongo.errors import DuplicateKeyError
import time


app = Flask(__name__)
CORS(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'faluyiisaiah@gmail.com'
app.config['MAIL_PASSWORD'] = "nawhobogecypovbo"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True   
mail = Mail(app)

bcrypt = Bcrypt(app)
Users_db = Usersdb()
OTP_db = OTPdb()
Solar_inverters_db = SolarInvertersdb()
Devices_db = Devicesdb()
DB_SS_db = DistributionBoardAndSmartSwitchesdb()

app.config['SECRET_KEY'] = "imolede"

@app.post('/api/v1/register/user')
def register():
    body = request.get_json()
    try:
    
        if "email" and "password" not in body:
            return {
                "status": "failed",
                "message": "Email and password are required"
            }, 400
            
        reg_details = {
            "name": body["name"],
            "imolede_id": body["imolede_id"],
            "email": body["email"],
            "phone": body["phone"],
            "state": body["state"],
            "LGA": body["LGA"],
            "address": body["address"],
            "password": generate_password_hash(body["password"]),
            "agreed_to_policy": body.get("agreed_to_policy", False),
            "created_at": datetime.now()
        }
        
        user_id = Users_db.create_user(reg_details)
        token = jwt.encode({
                "user_id": str(user_id),
            }, app.config["SECRET_KEY"], algorithm="HS256")
        return jsonify({"status": "success",
                        "message": "User registered successfully",
                       "data":{
                           "token": token
                                }}), 200
        
    except DuplicateKeyError:
        return {
            "status": "failed",
            "message": "Email address or Imolede ID already in use"
        }, 400
        
    
    except Exception as e:
        return jsonify({
            "status": "failed",
            "message": str(e),
        }), 500
        
@app.get('/api/v1/user')
@token_required
def update_user_profile(current_user):    
    try:
        
        return {
            "status": "success",
            "message": "User profile fecthed successfully",
            "data": {
                "user_profile": current_user},
        }, 200
        
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }, 500
        
@app.patch('/api/v1/user')
@token_required
def fetch_user_profile(current_user):    
    try:
        body = request.get_json()
        
        Users_db.update_user(current_user["_id"], body)
        
        return {
            "status": "success",
            "message": "User profile updated successfully"
        }, 200
        
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }, 500
        
        
@app.post('/api/v1/otp/generate')
def generate_otp():
    
    try: 
        email = request.json.get('email')
        if not email:
            return jsonify({"status":"failed",
                            "message": "email is required"
                            }), 400

        otp = pyotp.random_base32()
        totp = pyotp.TOTP(otp).now()[:4]

        expiration_time = datetime.now() + timedelta(minutes=5)

        OTP_db.update_otp(email, totp, expiration_time)
        
        msg = Message('ImoleDe OTP verification', sender = 'faluyiisaiah@gmail.com', recipients=[email])
        msg.body = f'OTP: {totp}'
        mail.send(msg)
        return jsonify({
            "status": "success",
            "message": "OTP generated and sent.",
            "data": {
                "otp": totp
                }}), 200
        
    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)}), 500

@app.post('/api/v1/otp/verify')
def verify_otp():
    
    try: 
        email = request.json.get('email')
        otp = request.json.get('otp')

        if not email or not otp:
            return jsonify({"status": "failed", "message": "User email and OTP are required"}), 400

        otp_record = OTP_db.get_otp(email)

        if not otp_record:
            return jsonify({"status": "failed", "message": "Record not found"}), 404

        if datetime.now() > otp_record['expiration_time']:
            OTP_db.delete_otp(email)  
            return jsonify({"status": "failed", "message": "OTP expired"}), 400

        if otp_record['otp'] != otp:
            return jsonify({"status": "failed", "message": "Invalid OTP"}), 400

        OTP_db.delete_otp({"email": email}) 
        return jsonify({"status": "success", "message": "OTP verified successfully!"}), 200
    
    except Exception as e:
        return jsonify({"status":"failed", "message":str(e)}), 500
    
        
@app.post("/api/v1/sign_in")
def sign_in():
    try:
    
        body = request.get_json()
        
        if "email" and "password" not in body:
            return {
                "status": "failed",
                "message": "Email and password are required"
            }, 400
        
        email = body["email"]
        password = body["password"] 
        
        user_profile = authenticate_user(email, password)
        
        if user_profile == "not found":
            return {
                "status": "failed",
                "message": "Invalid email address!"
            }, 404
            
        if not user_profile:
            return {
                "status": "failed",
                "message": "Invalid password!"
            }, 401
            
        token = jwt.encode({
            "user_id": str(user_profile["_id"]),
        }, app.config["SECRET_KEY"], algorithm="HS256")
                                                        
        return jsonify({
            "status": "success",
            "message": "Authentication successful",
            "data": {
                "token": token,
            }
            }), 200
        
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e),
        }, 500
        
        
@app.post('/api/v1/register/inverter')
@token_required
def register_solar_inverter(current_user):
    
    try:
        body = request.get_json()
        
        registration_details = {
            "size": body["size"],
            "maker": body["maker"],
            "model": body["model"],
            "number": body["number"],
            "rating": body["rating"],
            "battery_type": body["battery_type"],
            "number_of_batteries": body["number_of_batteries"],
            "battery_rating": body["battery_rating"],
            "cc_type": body["cc_type"],
            "cc_rating": body["cc_rating"],
            "user_id": current_user["_id"],
            "imolede_id": current_user["imolede_id"],
        }
        
        Solar_inverters_db.create(registration_details)
        
        return {
            "status": "success",
            "message": "Registration successful"
        }, 200
        
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }, 500
    
@app.get('/api/v1/inverter')
@token_required
def fetch_inverter(current_user):
    
    try:
       
        inverter = Solar_inverters_db.get_inverter(current_user["imolede_id"])
        del inverter["_id"]
        
        return {
            "status": "success",
            "message": "Data fetched successfully",
            "data": {
                "inverter": inverter
            }
        }, 200
        
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }, 500


@app.post('/api/v1/register/dbss')
@token_required
def register_dbss(current_user):
    
    try:
        body = request.get_json()
        
        registration_details = {
            "db_model": body["db_model"],
            "db_size": body["db_size"],
            "ss_num": body["ss_num"],
            "user_id": current_user["_id"],
            "imolede_id": current_user["imolede_id"],
        }
        
        DB_SS_db.create(registration_details)
        
        return {
            "status": "success",
            "message": "Registration successful"
        }, 200
        
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }, 500


@app.get('/api/v1/dbss')
@token_required
def fetch_dbss(current_user):
    
    try:
       
        dbss = DB_SS_db.get_dbss(current_user["imolede_id"])
        del dbss["_id"]
        
        return {
            "status": "success",
            "message": "Data fetched successfully",
            "data": {
                "dbss": dbss
            }
        }, 200
        
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }, 500

@app.post('/api/v1/register/devices')
@token_required
def register_device(current_user):
    
    try:
        body = request.get_json()
        
        registration_details = {
            "1": {
                "name": body['1']['name'],
                "state": "off",
                "wattage": body['1']['wattage']
            },
            "2": {
                "name": body['2']['name'],
                "state": "off",
                "wattage": body['2']['wattage']
            },
            "3": {
                "name": body['3']['name'],
                "state": "off",
                "wattage": body['3']['wattage']
            },
            "4": {
                "name": body['4']['name'],
                "state": "off",
                "wattage": body['4']['wattage']
            },
            "user_id": current_user["_id"],
            "imolede_id": current_user["imolede_id"],
            "created_at": datetime.now(),
        }
        
        Devices_db.create(registration_details)
        
        return {
            "status": "success",
            "message": "Registration successful"
        }, 200
        
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }, 500


@app.patch('/api/v1/device/state')
@token_required
def update_device_state(current_user):  
    try:
        body = request.get_json()
        
        Devices_db.update_device_state(current_user["imolede_id"], body["device"], body["state"])
        return {
            "status": "success",
            "message": "Device state updated successfully"
        }, 200
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }, 500   
    
@app.get('/api/v1/devices')
@token_required
def get_user_devices(current_user):
      
    try:
        
        devices =  Devices_db.get_user_devices(current_user["imolede_id"])
        del devices["_id"]
        return {
            "status": "success",
            "message": "Data fetched successfully",
            "data": {
                "devices": devices
            }
        }, 200
        
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }, 500
        
        
        
if __name__ == "__main__":
    app.run()