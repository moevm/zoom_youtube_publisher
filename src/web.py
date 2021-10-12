import json
import logging
import time

import click

from threading import Thread

from flask import Flask, request, redirect, render_template
from flask_socketio import SocketIO, emit

from message import Message


class WebThread(Thread):

    def __init__(self, zoom_auth_url, youtube_auth_url, codes_queue, message_queue):
        Thread.__init__(self)

        self.zoom_auth_url = zoom_auth_url
        self.youtube_auth_url = youtube_auth_url

        self.codes_queue = codes_queue
        self.message_queue = message_queue

        self.message = Message()

    def run(self) -> None:
        app = Flask(__name__)
        socketio = SocketIO(app)

        # logging.disable()

        def echo(*args, **kwargs): pass
        def secho(*args, **kwargs): pass

        click.echo = echo
        click.secho = secho

        @app.route("/zoom")
        def zoom_handler():

            zoom_code = request.args.get("code")
            self.codes_queue.put(zoom_code)

            return redirect(self.youtube_auth_url)

        @app.route("/youtube")
        def youtube_handler():

            youtube_code = request.args.get("code")
            self.codes_queue.put(youtube_code)

            return redirect("/")

        @app.route("/logs")
        def logs():
            with open('logs/app.log') as entries:
                return render_template("logs.html",
                                       title="Zoom Youtube Publisher Logs",
                                       logs=map(json.loads, entries))

        @app.route("/")
        def watch_handler():
            return render_template("index.html", status=self.message.status)

        @socketio.event
        def get_status():
            emit("status", {
                "status": self.message.status,
                "progress": {
                    "value": self.message.progress[0],
                    "max": self.message.progress[1]
                },
                "end": self.message.end
            })

        server = Thread(target=lambda: socketio.run(app, host="0.0.0.0", port=7034), daemon=True)
        server.start()

        while not self.message.end:

            self.message = self.message_queue.get()
            socketio.emit("status_changed", {
                "status": self.message.status,
                "progress": {
                    "value": self.message.progress[0],
                    "max": self.message.progress[1]
                },
                "end": self.message.end
            })

        time.sleep(2)
