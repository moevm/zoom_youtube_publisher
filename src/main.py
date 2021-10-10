import time
from queue import Queue
import json
import os
import signal
import sys

from appthreads import PublisherThread
from appthreads import WebThread
from schedulers import SafeScheduler
from signals import on_signal
from youtube import YoutubeClient
from zoom import ZoomClient


if __name__ == '__main__':

    zoom = ZoomClient(os.environ["ZOOM_CLIENT_ID"], os.environ["ZOOM_CLIENT_SECRET"])
    youtube = YoutubeClient(os.environ["YOUTUBE_CLIENT_ID"], os.environ["YOUTUBE_CLIENT_SECRET"])

    code_queue = Queue()
    message_queue = Queue()

    web = WebThread(zoom.get_authorize_code_url(), youtube.get_authorize_code_url(),
                    code_queue, message_queue)
    web.start()

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

    scheduler = SafeScheduler()

    @on_signal
    def clear_schedule(s):
        s.clear()
        sys.exit(0)

    def publish_job():
        publisher = PublisherThread(zoom, youtube, message_queue)
        publisher.daemon = True
        publisher.start()
        publisher.join()
        print("Published")

    sigterm_handler = clear_schedule(scheduler)
    signal.signal(signal.SIGTERM, sigterm_handler)

    scheduler.every(5).minutes.do(publish_job)
    scheduler.run_all()
    while True:
        scheduler.run_pending()
        time.sleep(1)
