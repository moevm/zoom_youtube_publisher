import json

from message import *


def build_oauth(zoom, youtube, code_queue, message_queue, logger, new=False):
    try:
        with open(".oauth2", "r") as f:
            oauth2_cache = json.load(f)
        zoom.use_cache(oauth2_cache)
        youtube.use_cache(oauth2_cache)
        print("Used cached tokens")
        logger.info("Used cached tokens")
    except FileNotFoundError:
        logger.info(".oauth2 not found")
        print("Please, visit:", zoom.get_authorize_code_url())
        if new:
            logger.info("Generating tokens")
            message_queue.put(Message(NO_TOKENS, link=(
                zoom.get_authorize_code_url(),
                "Создание токенов"
            )))
        else:
            logger.info("Refreshing tokens")

        zoom_code = code_queue.get()
        youtube_code = code_queue.get()

        zoom.login(zoom_code)
        youtube.login(youtube_code)

        logger.info(".oauth2 created")

    oauth2_cache = {
        "zoom_access_token": zoom.access_token,
        "zoom_refresh_token": zoom.refresh_token,
        "youtube_access_token": youtube.access_token,
        "youtube_refresh_token": youtube.refresh_token
    }
    with open(".oauth2", "w") as f:
        json.dump(oauth2_cache, f)
