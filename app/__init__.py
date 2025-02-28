# app/__init__.py
import datetime
import os
import logging
from flask import Flask
from flask_session import Session
from app.models.db import Database

db = Database()
session = Session()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)


    # Базовая конфигурация
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_replace_in_production'),
        DATABASE=os.path.join(app.instance_path, 'litvideo.db'),
        UPLOAD_FOLDER=os.path.join(app.static_folder, 'uploads'),
        SESSION_TYPE='filesystem',
        SESSION_PERMANENT=False,
        SESSION_USE_SIGNER=True,
        MAX_CONTENT_LENGTH=500 * 1024 * 1024  # 500 MB
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    # Настройка директорий для загрузок
    basedir = os.path.abspath(os.path.dirname(__file__))
    upload_folder = os.path.join(basedir, 'static', 'uploads')
    videos_dir = os.path.join(upload_folder, 'videos')
    thumbnails_dir = os.path.join(upload_folder, 'thumbnails')
    os.makedirs(videos_dir, exist_ok=True)
    os.makedirs(thumbnails_dir, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder

    # Инициализация сессий
    session.init_app(app)

    # Инициализация базы данных
    with app.app_context():
        db.init_app(app)

    # Регистрация маршрутов
    from app.routes import auth, video, comment
    app.register_blueprint(auth.bp)
    app.register_blueprint(video.bp)
    app.register_blueprint(comment.bp)  # Убедитесь, что в app/routes/comment.py определён bp

    @app.context_processor
    def inject_user():
        from app.models.user import User  # Импорт внутри функции
        return dict(User=User)

    @app.template_filter('humanize_time')
    def humanize_time(dt):
        """
        Returns string representing "time since" e.g.
        3 days ago, 5 hours ago etc.
        """

        if not isinstance(dt, datetime.datetime):
            return ""

        now = datetime.datetime.now()
        diff = now - dt

        periods = (
            (diff.days / 365.25, "year"),
            (diff.days / 30.44, "month"),
            (diff.days / 7, "week"),
            (diff.days, "day"),
            (diff.seconds / 3600, "hour"),
            (diff.seconds / 60, "minute"),
            (diff.seconds, "second"),
        )

        for period, name in periods:
            if abs(period) >= 1:
                period = round(period)
                if period != 1:
                    name += "s"
                return "%d %s ago" % (period, name)

        return "now"

    logging.basicConfig(level=logging.INFO)

    return app
