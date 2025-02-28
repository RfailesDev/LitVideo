# app/routes/comment.py
from flask import Blueprint, request, redirect, url_for, flash, session
from app.models.comment import Comment
from app.routes.auth import login_required

bp = Blueprint('comment', __name__, url_prefix='/comment')

@bp.route('/add/<int:video_id>', methods=['POST'])
@login_required
def add_comment(video_id):
    content = request.form.get('content')
    if not content or len(content.strip()) == 0:
        flash('Комментарий не может быть пустым')
        return redirect(url_for('video.view_video', video_id=video_id))
    user_id = session['user_id']
    try:
        Comment.create(video_id, user_id, content)
        flash('Комментарий добавлен')
    except Exception:
        flash('Не удалось добавить комментарий')
    return redirect(url_for('video.view_video', video_id=video_id))
