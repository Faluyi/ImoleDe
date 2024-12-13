from flask import Flask, request, jsonify, session
from flask_mail import Mail, Message
from db.models import *
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
Users_db = Userdb()
OTP_db = OTPdb()

app.config['SECRET_KEY'] = "imolede"

@app.post('/api/v1/register')
def register():
    body = request.get_json()
    try:
    
        if "email" and "password" not in body:
            return {
                "status": "failed",
                "message": "Email and password are required"
            }, 400
            
        reg_details = {
            "imolede_id": body["imolede_id"],
            "email": body["email"],
            "phone": body["phone"],
            "state": body["state"],
            "LGA": body["LGA"],
            "address": body["address"],
            "password": body["password"],
            "agreed_to_policy": body["agreed_to_policy", False],
            "created": datetime.now(),
        }
        
        user_id = Users_db.create_user(reg_details)
        token = jwt.encode({
                "user_id": str(user_id),
            }, app.config["SECRET_KEY"], algorithm="HS256")
        app.logger.info(token)
        return jsonify({"status": "success",
                        "message": "User registered successfully",
                       "data":{
                           "token": token
                                }}), 200
        
    except DuplicateKeyError:
        return {
            "status": "failed",
            "message": "Email address already in use"
        }, 400
        
    
    except Exception as e:
        return jsonify({
            "status": "failed",
            "message": str(e),
        }), 500
        
        
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

# Verify OTP
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
        app.logger.info(token)
                                                        
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

@app.get('/api/v1/user')
@token_required
def current_user_profile(current_user):    
    try:
        
        return {
            "status": "success",
            "message": "User profile fecthed successfully",
            "data": {
                "user_profile": current_user},
        }, 200
        
    except:
        return {
            "status": "failed",
            "message": "Internal server error"
        }, 500
        
        
        
if __name__ == "__main__":
    app.run()