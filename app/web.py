import json
import logging
import time

import click

from threading import Thread

from flask import request, redirect, render_template
from flask_socketio import SocketIO, emit

from message import Message


class WebThread(Thread):

    def __init__(self, app, zoom_auth_url, youtube_auth_url, codes_queue, message_queue):
        Thread.__init__(self)

        self.app = app
        self.zoom_auth_url = zoom_auth_url
        self.youtube_auth_url = youtube_auth_url

        self.codes_queue = codes_queue
        self.message_queue = message_queue

        self.message = Message()

    def run(self) -> None:
        socketio = SocketIO(self.app)

        # logging.disable()

        def echo(*args, **kwargs): pass
        def secho(*args, **kwargs): pass

        click.echo = echo
        click.secho = secho

        @self.app.route("/zoom")
        def zoom_handler():

            zoom_code = request.args.get("code")
            self.codes_queue.put(zoom_code)

            return redirect(self.youtube_auth_url)

        @self.app.route("/youtube")
        def youtube_handler():

            youtube_code = request.args.get("code")
            self.codes_queue.put(youtube_code)

            return redirect("/")

        @self.app.route("/logs")
        def logs():
            with open('logs/app.log') as entries:
                return render_template("logs.html",
                                       title="Zoom Youtube Publisher Logs",
                                       logs=map(json.loads, entries))

        @self.app.route("/")
        def watch_handler():
            return render_template("index.html", status=self.message.status, link=self.message.link)

        @socketio.event
        def get_status():
            emit("status", {
                "status": self.message.status,
                "progress": {
                    "value": self.message.progress[0],
                    "max": self.message.progress[1]
                },
                "end": self.message.end,
                "link": {
                    'href': self.message.link[0],
                    'text': self.message.link[1]
                }
            })

        server = Thread(target=lambda: socketio.run(self.app, host="0.0.0.0", port=7034), daemon=True)
        server.start()

        while not self.message.end:

            self.message = self.message_queue.get()
            socketio.emit("status_changed", {
                "status": self.message.status,
                "progress": {
                    "value": self.message.progress[0],
                    "max": self.message.progress[1]
                },
                "end": self.message.end,
                "link": {
                    'href': self.message.link[0],
                    'text': self.message.link[1]
                }
            })

        time.sleep(2)
