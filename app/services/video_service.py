# app/services/video_service.py
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from app.models.video import Video
from app.services.thumbnail_service import generate_thumbnail

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_video(file, title, description, user_id):
    if not file or not allowed_file(file.filename):
        return False, "Неподдерживаемый формат файла"

    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"

    with current_app.app_context():
        videos_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos')
        thumbnails_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'thumbnails')
        video_path = os.path.join(videos_dir, unique_filename)
        try:
            file.save(video_path)
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")
            return False, "Ошибка при сохранении файла"

        thumbnail_filename = f"{uuid.uuid4().hex}.jpg"
        thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
        if not generate_thumbnail(video_path, thumbnail_path):
            os.remove(video_path)
            return False, "Не удалось создать превью для видео"

        Video.create(title, description, unique_filename, thumbnail_filename, user_id)

    return True, "Видео успешно загружено"

def get_video_info(video_id):
    from app.models.video import Video
    video = Video.get_by_id(video_id)
    if not video:
        return None
    video_dict = dict(video)
    video_dict['video_url'] = f"/static/uploads/videos/{video['filepath']}"
    video_dict['thumbnail_url'] = f"/static/uploads/thumbnails/{video['thumbnail']}"
    return video_dict

def get_all_videos(page=1, per_page=12):
    from app.models.video import Video
    offset = (page - 1) * per_page
    videos = Video.get_all(limit=per_page, offset=offset)
    formatted_videos = []
    for video in videos:
        video_dict = dict(video)
        video_dict['thumbnail_url'] = f"/static/uploads/thumbnails/{video['thumbnail']}"
        formatted_videos.append(video_dict)
    return formatted_videos

def search_videos(query, page=1, per_page=12):
    """Поиск видео по названию и описанию."""
    from app.models.video import Video
    offset = (page - 1) * per_page
    # Важно использовать параметризованный запрос для защиты от SQL-инъекций.
    # Использование LIKE и % позволяет искать частичные совпадения.
    videos = Video.search(query, limit=per_page, offset=offset)  # Вызываем метод search у модели
    formatted_videos = []
    for video in videos:
        video_dict = dict(video)
        video_dict['thumbnail_url'] = f"/static/uploads/thumbnails/{video['thumbnail']}"
        formatted_videos.append(video_dict)
    return formatted_videos