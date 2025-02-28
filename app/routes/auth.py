# app/routes/auth.py
import functools
import os
import uuid
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, send_from_directory, current_app, jsonify
from app.models.user import User
from werkzeug.utils import secure_filename

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None
        if not username:
            error = 'Требуется имя пользователя'
        elif not password:
            error = 'Требуется пароль'
        elif User.get_by_username(username):
            error = 'Пользователь с таким именем уже существует'
        if error is None:
            User.create(username, password)
            flash('Регистрация успешна! Теперь вы можете войти.')
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None
        if not username:
            error = 'Требуется имя пользователя'
        elif not password:
            error = 'Требуется пароль'
        elif not User.verify_password(username, password):
            error = 'Неверное имя пользователя или пароль'
        if error is None:
            user = User.get_by_username(username)
            session.clear()
            session['user_id'] = user['id']
            session['username'] = username
            return redirect(url_for('video.index'))
        flash(error)
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('video.index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.get_by_id(user_id)
    if not user:
        flash('Пользователь не найден')
        return redirect(url_for('video.index'))

    user_videos = User.get_user_videos(user_id)
    formatted_videos = []
    for video in user_videos:
        video_dict = dict(video)
        video_dict['thumbnail_url'] = f"/static/uploads/thumbnails/{video['thumbnail']}"
        formatted_videos.append(video_dict)

    subscribers_count = User.get_subscribers_count(user_id)
    subscriptions_count = User.get_subscriptions_count(user_id)
    is_current_user = 'user_id' in session and session['user_id'] == user_id
    is_subscribed = False
    if 'user_id' in session and not is_current_user:
        is_subscribed = User.is_subscribed(session['user_id'], user_id)


    return render_template('profile.html', user=user, videos=formatted_videos, User=User,
                           subscribers_count=subscribers_count, subscriptions_count=subscriptions_count,
                           is_current_user=is_current_user, is_subscribed=is_subscribed)


@bp.route('/profile/<int:user_id>/upload_avatar', methods=['POST'])
@login_required
def upload_avatar(user_id):
    # Проверка прав доступа
    if session['user_id'] != user_id:
        flash('У вас нет прав для изменения этого профиля.')
        return redirect(url_for('auth.profile', user_id=user_id))

    # Проверка наличия файла в запросе
    if 'avatar' not in request.files:
        flash('Файл не выбран.')
        return redirect(url_for('auth.profile', user_id=user_id))

    file = request.files['avatar']
    if file.filename == '':
        flash('Файл не выбран.')
        return redirect(url_for('auth.profile', user_id=user_id))

    # Проверка допустимого формата файла
    if not allowed_file(file.filename):
        flash('Недопустимый формат файла. Разрешены только jpg, jpeg, png, gif.')
        return redirect(url_for('auth.profile', user_id=user_id))

    # Проверка размера файла (максимум 5MB)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    if file_size > 5 * 1024 * 1024:
        flash('Файл слишком большой. Максимальный размер 5MB.')
        return redirect(url_for('auth.profile', user_id=user_id))
    file.seek(0)  # Возвращаем указатель в начало файла

    # Генерация уникального имени файла
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"

    # Сохранение файла
    avatars_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
    os.makedirs(avatars_dir, exist_ok=True)
    avatar_path = os.path.join(avatars_dir, unique_filename)

    try:
        file.save(avatar_path)
        User.set_avatar(user_id, unique_filename)
        flash('Аватар успешно обновлен.')
    except Exception as e:
        current_app.logger.error(f"Ошибка при сохранении аватара: {e}")
        flash('Не удалось сохранить аватар.')
        return redirect(url_for('auth.profile', user_id=user_id))

    return redirect(url_for('auth.profile', user_id=user_id))

def allowed_file(filename):
    """Проверка допустимых расширений файла."""
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/static/uploads/avatars/<filename>')
def serve_avatar(filename):
    return send_from_directory(os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars'), filename)

@bp.route('/profile/<int:user_id>/subscribe', methods=['POST'])
@login_required
def subscribe(user_id):
    subscriber_id = session['user_id']
    if subscriber_id == user_id:
        return jsonify({'status': 'error', 'message': 'Нельзя подписаться на себя'}), 400
    if User.is_subscribed(subscriber_id, user_id):
        User.unsubscribe(subscriber_id, user_id)
        action = 'unsubscribe'
    else:
        User.subscribe(subscriber_id, user_id)
        action = 'subscribe'
    return jsonify({'status': 'success', 'action': action})