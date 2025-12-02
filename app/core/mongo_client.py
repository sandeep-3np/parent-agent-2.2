# app/core/mongo_client.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "MortgageAI")
LOS_COLLECTION = os.getenv("LOS_COLLECTION", "LOS")
TITLE_COLLECTION = os.getenv("TITLE_COLLECTION", "Title")
APPRAISAL_COLLECTION = os.getenv("APPRAISAL_COLLECTION", "Appraisal")
CREDIT_COLLECTION = os.getenv("CREDIT_COLLECTION", "CreditReport")
DRIVE_COLLECTION = os.getenv("DRIVE_COLLECTION", "DriveReport")

class MongoClientWrapper:
    def __init__(self, uri: str = None, db_name: str = None):
        self.client = MongoClient(uri or MONGO_URI)
        self.db = self.client[db_name or MONGO_DB]

    def get_los(self, loan_id):
        return self.db[LOS_COLLECTION].find_one({'loan_id': loan_id}) or {}

    def get_title(self, loan_id):
        return self.db[TITLE_COLLECTION].find_one({'loan_id': loan_id}) or {}

    def get_appraisal(self, loan_id):
        return self.db[APPRAISAL_COLLECTION].find_one({'loan_id': loan_id}) or {}

    def get_credit(self, loan_id):
        return self.db[CREDIT_COLLECTION].find_one({'loan_id': loan_id}) or {}

    def get_drive(self, loan_id):
        return self.db[DRIVE_COLLECTION].find_one({'loan_id': loan_id}) or {}
