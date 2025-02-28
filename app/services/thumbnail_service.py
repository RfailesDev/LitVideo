# app/services/thumbnail_service.py
import subprocess
import os

def generate_thumbnail(video_path, thumbnail_path):
    try:
        command = [
            'ffmpeg',
            '-i', video_path,
            '-ss', '00:00:05',
            '-vframes', '1',
            thumbnail_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return os.path.exists(thumbnail_path)
    except Exception as e:
        print(f"Ошибка при создании превью: {str(e)}")
        return False
