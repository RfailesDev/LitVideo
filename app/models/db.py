# app/models/db.py
import sqlite3
from flask import current_app, g

class Database:
    def init_app(self, app):
        app.teardown_appcontext(self.close_db)
        self.init_db()

    def get_db(self):
        if 'db' not in g:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_db(self, e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    def init_db(self):
        db = self.get_db()

        # Таблица пользователей
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                avatar TEXT
            )
        ''')

        # Таблица видео
        db.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                filepath TEXT NOT NULL,
                thumbnail TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                dislikes INTEGER DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Таблица комментариев
        db.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                comment TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Таблица для хранения лайков/дизлайков
        db.execute('''
            CREATE TABLE IF NOT EXISTS video_likes (
                user_id INTEGER NOT NULL,
                video_id INTEGER NOT NULL,
                like_type INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, video_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (video_id) REFERENCES videos (id)
            )
        ''')

        # Таблица подписок
        db.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscriber_id INTEGER NOT NULL,
                subscribed_to_id INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (subscriber_id, subscribed_to_id),
                FOREIGN KEY (subscriber_id) REFERENCES users (id),
                FOREIGN KEY (subscribed_to_id) REFERENCES users (id)
            )
        ''')

        db.commit()


    def query_db(self, query, args=(), one=False):
        cur = self.get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

    def execute_db(self, query, args=()):
        db = self.get_db()
        db.execute(query, args)
        db.commit()