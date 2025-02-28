# app/models/video.py
from app import db

class Video:
    @staticmethod
    def create(title, description, filepath, thumbnail, user_id):
        db.execute_db(
            'INSERT INTO videos (title, description, filepath, thumbnail, user_id) VALUES (?, ?, ?, ?, ?)',
            (title, description, filepath, thumbnail, user_id)
        )

    @staticmethod
    def get_by_id(video_id):
        return db.query_db(
            'SELECT v.*, u.username as author FROM videos v JOIN users u ON v.user_id = u.id WHERE v.id = ?',
            (video_id,),
            one=True
        )

    @staticmethod
    def get_all(limit=20, offset=0):
        return db.query_db(
            'SELECT v.*, u.username as author FROM videos v JOIN users u ON v.user_id = u.id ORDER BY v.created_at DESC LIMIT ? OFFSET ?',
            (limit, offset)
        )

    @staticmethod
    def get_related(video_id, limit=5):
        return db.query_db(
            'SELECT v.*, u.username as author FROM videos v JOIN users u ON v.user_id = u.id WHERE v.id != ? ORDER BY v.created_at DESC LIMIT ?',
            (video_id, limit)
        )

    @staticmethod
    def increment_views(video_id):
        db.execute_db(
            'UPDATE videos SET views = views + 1 WHERE id = ?',
            (video_id,)
        )

    @staticmethod
    def get_likes_count(video_id):
        result = db.query_db(
            'SELECT COUNT(*) as count FROM video_likes WHERE video_id = ? AND like_type = 1',
            (video_id,),
            one=True
        )
        return result['count'] if result else 0

    @staticmethod
    def get_dislikes_count(video_id):
        result = db.query_db(
            'SELECT COUNT(*) as count FROM video_likes WHERE video_id = ? AND like_type = -1',
            (video_id,),
            one=True
        )
        return result['count'] if result else 0

    @staticmethod
    def has_user_liked(video_id, user_id):
        return db.query_db(
            'SELECT 1 FROM video_likes WHERE video_id = ? AND user_id = ? AND like_type = 1',
            (video_id, user_id),
            one=True
        ) is not None

    @staticmethod
    def has_user_disliked(video_id, user_id):
        return db.query_db(
            'SELECT 1 FROM video_likes WHERE video_id = ? AND user_id = ? AND like_type = -1',
            (video_id, user_id),
            one=True
        ) is not None

    @staticmethod
    def set_like(video_id, user_id, like_type):
        # Сначала пытаемся удалить существующую запись (если пользователь меняет лайк на дизлайк или наоборот)
        db.execute_db('DELETE FROM video_likes WHERE video_id = ? AND user_id = ?', (video_id, user_id))

        # Добавляем новую запись
        db.execute_db(
            'INSERT INTO video_likes (video_id, user_id, like_type) VALUES (?, ?, ?)',
            (video_id, user_id, like_type)
        )

        # Обновляем счетчики в таблице videos
        if like_type == 1:
            db.execute_db('UPDATE videos SET likes = likes + 1 WHERE id = ?', (video_id,))
        else:
            db.execute_db('UPDATE videos SET dislikes = dislikes + 1 WHERE id = ?', (video_id,))

    @staticmethod
    def remove_like(video_id, user_id):
        like_type_query = db.query_db('SELECT like_type from video_likes WHERE video_id = ? AND user_id = ?',
                                      (video_id, user_id), one=True)

        if like_type_query is None:
            return  # ничего не делаем, если пользователь не ставил лайк

        like_type = like_type_query['like_type']
        # Удаляем запись из video_likes
        db.execute_db('DELETE FROM video_likes WHERE video_id = ? AND user_id = ?', (video_id, user_id))

        # Обновляем счетчики в таблице videos
        if like_type == 1:
            db.execute_db('UPDATE videos SET likes = likes - 1 WHERE id = ?', (video_id,))
        else:
            db.execute_db('UPDATE videos SET dislikes = dislikes - 1 WHERE id = ?', (video_id,))

    @staticmethod
    def search(query, limit=20, offset=0):
        """Поиск видео по названию и описанию."""
        query_str = f"%{query}%"  # Добавляем % для поиска подстроки
        return db.query_db(
            'SELECT v.*, u.username as author FROM videos v JOIN users u ON v.user_id = u.id WHERE v.title LIKE ? OR v.description LIKE ? ORDER BY v.created_at DESC LIMIT ? OFFSET ?',
            (query_str, query_str, limit, offset)
        )