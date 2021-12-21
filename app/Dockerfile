FROM python:3

RUN adduser --disabled-password --gecos '' zoom_youtube_publisher

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

RUN chmod 777 -R /app
RUN chown -R zoom_youtube_publisher:zoom_youtube_publisher ./



CMD [ "python", "main.py" ]
