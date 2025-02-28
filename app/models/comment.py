# app/models/comment.py
from app import db

class Comment:
    @staticmethod
    def create(video_id, user_id, comment_text):
        db.execute_db(
            'INSERT INTO comments (video_id, user_id, comment) VALUES (?, ?, ?)',
            (video_id, user_id, comment_text)
        )

    @staticmethod
    def get_by_video(video_id):
        return db.query_db(
            'SELECT c.*, u.username as author, u.avatar as avatar FROM comments c JOIN users u ON c.user_id = u.id WHERE c.video_id = ? ORDER BY c.created_at ASC',
            (video_id,)
        )
