from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId 
from properties import *
import string, random

uri_web = os.getenv("DB_URI")
uri_local = "localhost:27017"
client = MongoClient(uri_web)
db = client['ImoleDe_DB']
Users = db["Users"]
OTP = db['User_otps']
Solar_inverters = db['Solar_inverters']
DBSS = db['Distribution_board_and_smart_switches']
Devices = db['Devices']
Users.create_index([('email', ASCENDING), ], unique=True)
Users.create_index([('imolede_id', ASCENDING), ], unique=True)

class Usersdb:
    def __init__(self) -> None:
        self.collection =  Users

    def create_user(self, details):  
        return self.collection.insert_one(details).inserted_id
        
    def get_active_users_by_role(self, role):
        return self.collection.find({"role": role, "active": True}).sort([('_id', -1)])
    
    def get_user_by_role_one(self, role):
        return self.collection.find_one({"role": role})
    
    def get_master_by_location(self, location):
        return self.collection.find_one({"role": "waste-master", "location": location, "active": True})
    
    def get_aggregators_by_location(self, location):
        return self.collection.find({"role": "waste-aggregator", "location": location, "active": True})
    
    def get_user_by_email(self, email):
        return self.collection.find_one({"email": email})
    
    def get_user_by_id(self, user_id):
        return self.collection.find_one({"_id": ObjectId(user_id)})
    
    def update_user(self, user_id, details):
       return self.collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": details}
    )

        
    
class OTPdb:
    def __init__(self) -> None:
        self.collection = OTP
           
    def create(self, dtls):
        return self.collection.insert_one(dtls).inserted_id

    def get_all(self):
        return self.collection.find().sort("date_time")
    
    def get_otp(self, email):
        return self.collection.find_one({"email": email})
    
    def delete_otp(self, email):
        return self.collection.delete_one({"email": email}).deleted_count>0
   
    def update_otp(self, email, totp, expiration_time):
       return self.collection.update_one(
        {"email": email},
        {"$set": {"otp": totp, "expiration_time": expiration_time}},
        upsert=True
    )
       
class SolarInvertersdb:
    def __init__(self) -> None:
        self.collection = Solar_inverters
           
    def create(self, dtls):
        return self.collection.insert_one(dtls).inserted_id

    def get_all(self):
        return self.collection.find().sort("date_time")
    
    def get_inverter(self, imolede_id):
        return self.collection.find_one({"imolede_id": imolede_id})
    
    def delete_otp(self, email):
        return self.collection.delete_one({"email": email}).deleted_count>0
   
    def update_otp(self, email, totp, expiration_time):
       return self.collection.update_one(
        {"email": email},
        {"$set": {"otp": totp, "expiration_time": expiration_time}},
        upsert=True
    )


class DistributionBoardAndSmartSwitchesdb:
    def __init__(self) -> None:
        self.collection = DBSS
           
    def create(self, dtls):
        return self.collection.insert_one(dtls).inserted_id

    def get_all(self):
        return self.collection.find().sort("date_time")
    
    def get_dbss(self, imolede_id):
        return self.collection.find_one({"imolede_id": imolede_id})
    
    def delete_otp(self, email):
        return self.collection.delete_one({"email": email}).deleted_count>0
   
    def update_otp(self, email, totp, expiration_time):
       return self.collection.update_one(
        {"email": email},
        {"$set": {"otp": totp, "expiration_time": expiration_time}},
        upsert=True
    )
       
       
class Devicesdb:
    def __init__(self) -> None:
        self.collection = Devices
           
    def create(self, dtls):
        return self.collection.insert_one(dtls).inserted_id

    def get_devices(self):
        return self.collection.find()
    
    def get_user_devices(self, imolede_id):
        return self.collection.find_one({"imolede_id": imolede_id})
    
    def delete_otp(self, email):
        return self.collection.delete_one({"email": email}).deleted_count>0
   
    def update_device_state(self, imolede_id, device, state):
       return self.collection.update_one(
        {"imolede_id": imolede_id},
        {"$set": {f"{device}.state": state}}
    )