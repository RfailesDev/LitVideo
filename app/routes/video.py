# app/routes/video.py
import os
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, send_from_directory, \
    current_app, jsonify
from app.models.user import User
from app.services.video_service import save_video, get_video_info, get_all_videos, search_videos  # Добавили search_videos
from app.routes.auth import login_required
from app.models.video import Video
from app.models.comment import Comment

bp = Blueprint('video', __name__)

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')  # Получаем поисковый запрос
    if query:
        videos = search_videos(query, page=page)  # Используем search_videos
    else:
        videos = get_all_videos(page=page)
    return render_template('index.html', videos=videos, page=page, query=query) # Передаём query в шаблон


@bp.route('/search')  # Этот маршрут больше не нужен, поиск обрабатывается в index
def search():
    return redirect(url_for('video.index', query=request.args.get('query', '')))


@bp.route('/upload', methods=('GET', 'POST'))
@login_required
def upload_video():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        file = request.files.get('video')
        error = None
        if not title:
            error = 'Требуется название видео'
        elif not file:
            error = 'Требуется выбрать файл'
        if error is None:
            user_id = session['user_id']
            success, message = save_video(file, title, description, user_id)
            if success:
                flash('Видео успешно загружено!')
                return redirect(url_for('video.index'))
            else:
                error = message
        flash(error)
    return render_template('upload.html')

@bp.route('/static/uploads/videos/<filename>')
def serve_video(filename):
    return send_from_directory(os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos'), filename)

@bp.route('/video/<int:video_id>')
def view_video(video_id):
    video = get_video_info(video_id)
    if not video:
        flash('Видео не найдено')
        return redirect(url_for('video.index'))
    Video.increment_views(video_id)
    comments = Comment.get_by_video(video_id)
    related_videos = Video.get_related(video_id)
    formatted_related = []
    for related in related_videos:
        related_dict = dict(related)
        related_dict['thumbnail_url'] = f"/static/uploads/thumbnails/{related['thumbnail']}"
        formatted_related.append(related_dict)
    video['comments'] = comments

    # Добавляем информацию о лайках и дизлайках
    video['likes'] = Video.get_likes_count(video_id)
    video['dislikes'] = Video.get_dislikes_count(video_id)

    # Проверяем, лайкнул/дизлайкнул ли текущий пользователь
    if 'user_id' in session:
        video['user_liked'] = Video.has_user_liked(video_id, session['user_id'])
        video['user_disliked'] = Video.has_user_disliked(video_id, session['user_id'])
    else:
        video['user_liked'] = False
        video['user_disliked'] = False

    return render_template('video.html', video=video, related_videos=formatted_related)


@bp.route('/video/<int:video_id>/like', methods=['POST'])
@login_required
def like_video(video_id):
    user_id = session['user_id']
    if Video.has_user_liked(video_id, user_id):
        Video.remove_like(video_id, user_id)
        action = 'remove_like'
    else:
        Video.set_like(video_id, user_id, 1)  # 1 - это like
        action = 'like'

    likes_count = Video.get_likes_count(video_id)
    dislikes_count = Video.get_dislikes_count(video_id)

    return jsonify({'status': 'success', 'action': action, 'likes': likes_count, 'dislikes': dislikes_count})


@bp.route('/video/<int:video_id>/dislike', methods=['POST'])
@login_required
def dislike_video(video_id):
    user_id = session['user_id']
    if Video.has_user_disliked(video_id, user_id):
        Video.remove_like(video_id, user_id)
        action = 'remove_dislike'
    else:
      Video.set_like(video_id, user_id, -1)  # -1 - это dislike
      action = 'dislike'

    likes_count = Video.get_likes_count(video_id)
    dislikes_count = Video.get_dislikes_count(video_id)

    return jsonify({'status': 'success', 'action': action, 'likes': likes_count, 'dislikes': dislikes_count})

@bp.route('/download/<filename>')
@login_required
def download_video(filename):
    """Маршрут для скачивания видео."""
    try:
        return send_from_directory(
            os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos'),
            filename,
            as_attachment=True
        )
    except FileNotFoundError:
        flash('Файл не найден')
        return redirect(url_for('video.index'))