"""
Authentication helpers: signup, login, session management.
Passwords are hashed with bcrypt before storage.
"""

import bcrypt
from datetime import datetime
from database import get_users_collection
import streamlit as st


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_user(username: str, email: str, password: str) -> dict:
    """
    Creates a new user. Returns {"success": True} or {"success": False, "error": "..."}.
    """
    col = get_users_collection()
    if col.find_one({"email": email}):
        return {"success": False, "error": "An account with this email already exists."}
    if col.find_one({"username": username}):
        return {"success": False, "error": "Username is already taken."}

    user = {
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "created_at": datetime.utcnow(),
    }
    result = col.insert_one(user)
    return {"success": True, "user_id": str(result.inserted_id)}


def login_user(email: str, password: str) -> dict:
    """
    Validates credentials. Returns user dict (without hash) on success.
    """
    col = get_users_collection()
    user = col.find_one({"email": email})
    if not user:
        return {"success": False, "error": "No account found with that email."}
    if not verify_password(password, user["password_hash"]):
        return {"success": False, "error": "Incorrect password."}

    return {
        "success": True,
        "user_id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
    }


def is_logged_in() -> bool:
    return st.session_state.get("authenticated", False)


def logout():
    for key in ["authenticated", "user_id", "username", "email"]:
        st.session_state.pop(key, None)
