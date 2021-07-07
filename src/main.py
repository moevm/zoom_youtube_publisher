from queue import Queue
import json
import os

from publisher import PublisherThread
from web import WebThread
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

    try:

        publisher = PublisherThread(zoom, youtube, message_queue)
        publisher.start()
        publisher.join()

    except Exception as e:
        print(e)

    oauth2_cache = {
        "zoom_access_token": zoom.access_token,
        "zoom_refresh_token": zoom.refresh_token,
        "youtube_access_token": youtube.access_token,
        "youtube_refresh_token": youtube.refresh_token
    }
    with open(".oauth2", "w") as f:
        json.dump(oauth2_cache, f)

