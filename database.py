"""
MongoDB connection and collection helpers.
All database operations are centralized here.
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

_client = None


def get_client():
    global _client
    if _client is None:
        uri = st.secrets.get("MONGODB_URI", os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _client


def get_db():
    client = get_client()
    db_name = st.secrets.get("MONGODB_DB", os.getenv("MONGODB_DB", "meal_recommendation_db"))
    return client[db_name]


def get_users_collection():
    return get_db()["users"]


def get_profiles_collection():
    return get_db()["profiles"]


def get_meals_collection():
    return get_db()["meals"]


def get_history_collection():
    return get_db()["recommendation_history"]


def check_connection():
    """Returns True if MongoDB is reachable."""
    try:
        get_client().admin.command("ping")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError):
        return False


def seed_meals_if_empty():
    """Populate meals collection from nutrition_data.csv if it is empty."""
    import pandas as pd

    col = get_meals_collection()
    if col.count_documents({}) > 0:
        return

    csv_path = os.path.join(os.path.dirname(__file__), "nutrition_data.csv")
    if not os.path.exists(csv_path):
        return

    df = pd.read_csv(csv_path)
    records = df.to_dict(orient="records")
    if records:
        col.insert_many(records)
