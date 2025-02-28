// app/static/js/video-player.js
document.addEventListener('DOMContentLoaded', () => {
    // Инициализация плеера Plyr с расширенными опциями
    const player = new Plyr('#player', {
        controls: [
            'play-large', // Большая кнопка воспроизведения в центре
            'restart', // Перезапуск воспроизведения
            'rewind', // Перемотка назад
            'play', // Воспроизведение/пауза
            'fast-forward', // Перемотка вперед
            'progress', // Прогресс-бар
            'current-time', // Текущее время
            'duration', // Общая продолжительность
            'mute', // Включение/выключение звука
            'volume', // Регулировка громкости
            'captions', // Субтитры (если доступны)
            'settings', // Настройки
            'pip', // Картинка в картинке
            'airplay', // AirPlay (для устройств Apple)
            'fullscreen' // Полноэкранный режим
        ],
        settings: ['captions', 'quality', 'speed', 'loop'],
        quality: {
            default: 720,
            options: [4320, 2880, 2160, 1440, 1080, 720, 576, 480, 360, 240]
        },
        speed: {
            selected: 1,
            options: [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3]
        },
        keyboard: {focused: true, global: true},
    });

    // Настройка автовоспроизведения следующего видео
    const autoplayToggle = document.querySelector('.autoplay-toggle');
    if (autoplayToggle) {
        // Проверяем сохраненное состояние автовоспроизведения
        const autoplay = localStorage.getItem('autoplay') === 'true';
        if (autoplay) {
            autoplayToggle.classList.add('active');
        }

        // Обработчик нажатия на переключатель автовоспроизведения
        autoplayToggle.addEventListener('click', () => {
            const isActive = autoplayToggle.classList.toggle('active');
            localStorage.setItem('autoplay', isActive);
        });

        // При завершении видео, если автовоспроизведение включено, перейти к следующему видео
        player.on('ended', event => {
            if (autoplayToggle.classList.contains('active')) {
                const nextVideo = document.querySelector('.related-videos .related-video-card');
                if (nextVideo) {
                    setTimeout(() => {
                        nextVideo.click();
                    }, 1000);
                }
            }
        });
    }

    // Обработчики для кнопок действий (лайк, дизлайк, сохранить, поделиться)
    document.querySelectorAll('.action-btn').forEach(button => {
        button.addEventListener('click', function () {
            if (this.classList.contains('like-btn') || this.classList.contains('dislike-btn')) {
                // Переключаем состояние кнопок лайка/дизлайка
                const isLike = this.classList.contains('like-btn');
                const otherBtn = isLike ?
                    document.querySelector('.dislike-btn') :
                    document.querySelector('.like-btn');

                if (this.classList.contains('active')) {
                    // Если кнопка уже активна, снимаем выделение
                    this.classList.remove('active');
                    this.style.background = '';
                    this.style.color = '';
                } else {
                    // Активируем кнопку
                    this.classList.add('active');
                    this.style.background = isLike ? '#def7e5' : '#f9e3e3';
                    this.style.color = isLike ? '#2e7d32' : '#d32f2f';

                    // Снимаем активность с противоположной кнопки
                    otherBtn.classList.remove('active');
                    otherBtn.style.background = '';
                    otherBtn.style.color = '';
                }
            } else if (this.classList.contains('share-btn')) {
                // Логика для кнопки поделиться
                if (navigator.share) {
                    navigator.share({
                        title: document.querySelector('.video-title').textContent,
                        url: window.location.href
                    }).catch(console.error);
                } else {
                    // Fallback для браузеров без Web Share API
                    prompt('Скопируйте ссылку:', window.location.href);
                }
            } else if (this.classList.contains('save-btn')) {
                // Логика для кнопки сохранить
                this.classList.toggle('active');
                if (this.classList.contains('active')) {
                    this.innerHTML = '<i class="fas fa-bookmark"></i> Сохранено';
                } else {
                    this.innerHTML = '<i class="far fa-bookmark"></i> Сохранить';
                }
            }
        });
    });

    // Показываем действия комментария при наведении
    const commentForm = document.querySelector('.comment-form');
    if (commentForm) {
        const textarea = commentForm.querySelector('textarea');
        const commentActions = commentForm.querySelector('.comment-actions');

        textarea.addEventListener('focus', () => {
            commentActions.style.opacity = '1';
            commentActions.style.visibility = 'visible';
        });

        textarea.addEventListener('blur', (e) => {
            if (!textarea.value.trim() && !commentActions.contains(e.relatedTarget)) {
                commentActions.style.opacity = '0';
                commentActions.style.visibility = 'hidden';
            }
        });

        const cancelBtn = commentForm.querySelector('.btn-cancel');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                textarea.value = '';
                textarea.blur();
                commentActions.style.opacity = '0';
                commentActions.style.visibility = 'hidden';
            });
        }
    }

    // Обработчики для кнопок комментариев
    document.querySelectorAll('.comment-like, .comment-dislike').forEach(button => {
        button.addEventListener('click', function () {
            const isLike = this.classList.contains('comment-like');
            const otherBtn = isLike ?
                this.nextElementSibling :
                this.previousElementSibling;

            if (this.classList.contains('active')) {
                // Если кнопка уже активна, снимаем выделение
                this.classList.remove('active');
            } else {
                // Активируем кнопку
                this.classList.add('active');

                // Снимаем активность с противоположной кнопки
                otherBtn.classList.remove('active');
            }
        });
    });

    // Инициализация показа/скрытия описания видео
    const descriptionText = document.querySelector('.video-description p');
    const showMoreBtn = document.querySelector('.show-more-btn');

    if (descriptionText && showMoreBtn) {
        // Проверяем, нужна ли кнопка "Показать больше"
        if (descriptionText.scrollHeight > descriptionText.clientHeight) {
            showMoreBtn.style.display = 'block';
            descriptionText.style.maxHeight = '80px';
            descriptionText.style.overflow = 'hidden';

            showMoreBtn.addEventListener('click', function () {
                if (descriptionText.style.maxHeight) {
                    descriptionText.style.maxHeight = null;
                    descriptionText.style.overflow = 'visible';
                    this.textContent = 'Свернуть';
                } else {
                    descriptionText.style.maxHeight = '80px';
                    descriptionText.style.overflow = 'hidden';
                    this.textContent = 'Показать больше';
                }
            });
        } else {
            showMoreBtn.style.display = 'none';
        }
    }

    // Функция для отправки AJAX-запроса
    function sendLikeDislikeRequest(videoId, action, button) {
        fetch(`/video/${videoId}/${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Обновляем количество лайков/дизлайков
                    document.querySelector('.like-btn .count').textContent = data.likes;
                    document.querySelector('.dislike-btn .count').textContent = data.dislikes;

                    // Обновляем состояние кнопок
                    const likeBtn = document.querySelector('.like-btn');
                    const dislikeBtn = document.querySelector('.dislike-btn');

                    if (data.action === 'like') {
                        likeBtn.classList.add('active');
                        likeBtn.querySelector('i').classList.remove('far');
                        likeBtn.querySelector('i').classList.add('fas');

                        dislikeBtn.classList.remove('active');
                        dislikeBtn.querySelector('i').classList.add('far');
                        dislikeBtn.querySelector('i').classList.remove('fas');

                    } else if (data.action === 'dislike') {
                        dislikeBtn.classList.add('active');
                        dislikeBtn.querySelector('i').classList.remove('far');
                        dislikeBtn.querySelector('i').classList.add('fas');


                        likeBtn.classList.remove('active');
                        likeBtn.querySelector('i').classList.add('far');
                        likeBtn.querySelector('i').classList.remove('fas');
                    } else if (data.action === 'remove_like') {
                        likeBtn.classList.remove('active');
                        likeBtn.querySelector('i').classList.add('far');
                        likeBtn.querySelector('i').classList.remove('fas');
                    } else if (data.action === 'remove_dislike') {
                        dislikeBtn.classList.remove('active');
                        dislikeBtn.querySelector('i').classList.add('far');
                        dislikeBtn.querySelector('i').classList.remove('fas');
                    }
                } else {
                    console.error('Ошибка при обработке лайка/дизлайка');
                }
            })
            .catch(error => {
                console.error('Ошибка при отправке запроса:', error);
            });
    }


    //Находим все кнопки like и dislike и вешаем на них обработчик
    document.querySelectorAll('.like-btn, .dislike-btn').forEach(button => {
        button.addEventListener('click', function () {
            const videoId = this.dataset.videoId;
            const action = this.dataset.action;
            sendLikeDislikeRequest(videoId, action, this);
        });
    });
});