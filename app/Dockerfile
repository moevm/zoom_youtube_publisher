FROM python:3

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

RUN chown -R zoom_youtube_publisher:zoom_youtube_publisher ./

CMD [ "python", "main.py" ]
