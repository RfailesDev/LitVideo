# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Установка FFmpeg.  Добавляем apt-get update и apt-get install -y ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 7071

CMD ["gunicorn", "--bind", "0.0.0.0:7071", "wsgi:app"]