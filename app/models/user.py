# app/models/user.py
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import os
from flask import current_app


class User:
    @staticmethod
    def create(username, password):
        hashed_password = generate_password_hash(password)
        db.execute_db(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, hashed_password)
        )

    @staticmethod
    def get_by_id(user_id):
        return db.query_db(
            'SELECT * FROM users WHERE id = ?',
            (user_id,),
            one=True
        )

    @staticmethod
    def get_by_username(username):
        return db.query_db(
            'SELECT * FROM users WHERE username = ?',
            (username,),
            one=True
        )

    @staticmethod
    def verify_password(username, password):
        user = User.get_by_username(username)
        if not user:
            return False
        return check_password_hash(user['password'], password)

    @staticmethod
    def set_avatar(user_id, avatar_filename):
        db.execute_db(
            'UPDATE users SET avatar = ? WHERE id = ?',
            (avatar_filename, user_id)
        )

    @staticmethod
    def get_avatar_url(user_id):
        user = User.get_by_id(user_id)
        if user and user['avatar']:
            return f"/static/uploads/avatars/{user['avatar']}"
        else:
            return "https://via.placeholder.com/40"  # Default avatar

    @staticmethod
    def get_user_videos(user_id):
        return db.query_db(
            'SELECT v.*, u.username as author FROM videos v JOIN users u ON v.user_id = u.id WHERE v.user_id = ? ORDER BY v.created_at DESC',
            (user_id,)
        )

    @staticmethod
    def get_subscribers_count(user_id):
        result = db.query_db(
            'SELECT COUNT(*) as count FROM subscriptions WHERE subscribed_to_id = ?',
            (user_id,),
            one=True
        )
        return result['count'] if result else 0

    @staticmethod
    def get_subscriptions_count(user_id):
        result = db.query_db(
            'SELECT COUNT(*) as count FROM subscriptions WHERE subscriber_id = ?',
            (user_id,),
            one=True
        )
        return result['count'] if result else 0

    @staticmethod
    def is_subscribed(subscriber_id, subscribed_to_id):
        return db.query_db(
            'SELECT 1 FROM subscriptions WHERE subscriber_id = ? AND subscribed_to_id = ?',
            (subscriber_id, subscribed_to_id),
            one=True
        ) is not None

    @staticmethod
    def subscribe(subscriber_id, subscribed_to_id):
        db.execute_db(
            'INSERT INTO subscriptions (subscriber_id, subscribed_to_id) VALUES (?, ?)',
            (subscriber_id, subscribed_to_id)
        )

    @staticmethod
    def unsubscribe(subscriber_id, subscribed_to_id):
        db.execute_db(
            'DELETE FROM subscriptions WHERE subscriber_id = ? AND subscribed_to_id = ?',
            (subscriber_id, subscribed_to_id)
        )