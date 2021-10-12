import logging
import threading
import time
import traceback
from queue import Queue
import json
import os
import signal
import sys

from publisher import PublisherThread
from logs import pull_logger
from web import WebThread
from safeschedule import SafeScheduler
from signalhandlers import on_signal
from youtube import YoutubeClient
from zoom import ZoomClient


def print_hook(args):
    app_logger.error(''.join(traceback.format_exception(args[0], args[1], args[2])))


def sys_hook(*args):
    print_hook(args)
    sys.__excepthook__(args[0], args[1], args[2])


if __name__ == '__main__':

    zoom = ZoomClient(os.environ["ZOOM_CLIENT_ID"], os.environ["ZOOM_CLIENT_SECRET"])
    youtube = YoutubeClient(os.environ["YOUTUBE_CLIENT_ID"], os.environ["YOUTUBE_CLIENT_SECRET"])

    code_queue = Queue()
    message_queue = Queue()

    app_logger = pull_logger("app", logging.INFO)

    threading.excepthook = print_hook

    sys.excepthook = sys_hook

    web = WebThread(zoom.get_authorize_code_url(), youtube.get_authorize_code_url(),
                    code_queue, message_queue)
    web.start()
    app_logger.info("App started")

    print("You can watch for a process on http://localhost:7034")

    try:
        with open(".oauth2", "r") as f:
            oauth2_cache = json.load(f)
        zoom.use_cache(oauth2_cache)
        youtube.use_cache(oauth2_cache)
        print("Used cached tokens")
    except FileNotFoundError:
        print("Please, visit:", zoom.get_authorize_code_url())

        zoom_code = code_queue.get()
        youtube_code = code_queue.get()

        zoom.login(zoom_code)
        youtube.login(youtube_code)

    oauth2_cache = {
        "zoom_access_token": zoom.access_token,
        "zoom_refresh_token": zoom.refresh_token,
        "youtube_access_token": youtube.access_token,
        "youtube_refresh_token": youtube.refresh_token
    }
    with open(".oauth2", "w") as f:
        json.dump(oauth2_cache, f)

    scheduler = SafeScheduler(logger=app_logger)

    @on_signal
    def clear_schedule(schedule):
        schedule.clear()
        app_logger.info("App shutdown")
        sys.exit(0)

    def publish_job(logger):
        publisher = PublisherThread(zoom, youtube, message_queue)
        logger.info("Started publishing thread")
        publisher.start()
        publisher.join()
        logger.info("Joined publishing thread")

    exit_handler = clear_schedule(scheduler)
    signal.signal(signal.SIGTERM, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)

    scheduler.every(5).minutes.do(publish_job, app_logger)
    scheduler.run_all()
    while True:
        scheduler.run_pending()
        time.sleep(1)
