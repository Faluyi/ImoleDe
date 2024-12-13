from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId 
from properties import *
import string, random
import requests

uri_web = os.getenv("Db_uri")
client = MongoClient(uri_web)
db = client['ImoleDe_DB']
Users = db["Users"]
OTP = db['User_otps']
Users.create_index([('email', ASCENDING)], unique=True)


class Userdb:
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
    
    def fs_get_user_by_id(self, user_id, token):
        url = f"https://app.foodsoldiers.io/api/v1/userdetail/{user_id}"
        headers = {
                    'Authorization': f'Bearer {token}',
                    }
        
        response = requests.get(url, headers=headers)
        return response.json()["data"]
    
    def get_pending_approvals(self):
        return self.collection.find({"status": "pending"}).sort([('_id', -1)])
    
    def get_disabled_users(self):
        return self.collection.find({"status": "Approved","active": False}).sort([('_id', -1)])
    
    def update_user_role(self, user_id, dtls):
        return self.collection.update_one({"uid":user_id},{"$set":dtls}).modified_count>0
    
    def update_user_profile(self, _id, dtls):
        return self.collection.update_one({"_id": ObjectId(_id)},{"$set":dtls}).modified_count>0
    
    def update_user_notifications(self, _id, dtls):
        return self.collection.update_one({"_id": ObjectId(_id)},{"$push": {"notifications": {"$each": [dtls], "$position": 0}}}).modified_count>0
        
    
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
