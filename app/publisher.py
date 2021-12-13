import os
import time
from threading import Thread
from urllib.error import HTTPError
from urllib.request import urlretrieve

from googleapiclient.errors import ResumableUploadError

from login import build_oauth

from message import *

HTTP_UNAUTHORIZED_CODE = 401
QUOTA_EXCEEDED_REASON = "quotaExceeded"


class PublisherThread(Thread):

    def __init__(self, zoom, youtube, message_queue, code_queue, logger):
        Thread.__init__(self)

        self.zoom = zoom
        self.youtube = youtube

        self.message_queue = message_queue
        self.code_queue = code_queue

        self.logger = logger

    def run(self) -> None:

        is_completed = False
        records = []

        meetings = set(map(int, os.environ["MEETING_ID"].split(" ")))

        while not is_completed:
            try:
                records, is_completed = self.zoom.get_records(meetings)
            except KeyError:
                self.message_queue.put(Message(INVALID_TOKENS, link=(
                    self.zoom.get_authorize_code_url(),
                    'Обновление токенов'
                )))
                self.logger.warning("Tokens were invalidated")
                os.remove(".oauth2")
                build_oauth(self.zoom, self.youtube, self.code_queue, self.message_queue)
                self.message_queue.put(Message(NEW_TOKENS))

                records, is_completed = self.zoom.get_records(meetings)

            if not is_completed:
                self.message_queue.put(Message(WAIT_FOR_COMPLETED_STATUS))
                time.sleep(10)

        for index, record in enumerate(records):

            self.message_queue.put(Message(DOWNLOADING_RECORDS_STATUS, (index, len(records))))
            title = record.get_video_name()

            try:
                urlretrieve(f"{record.download_url}?access_token={self.zoom.access_token}", f"{title}.mp4")
            except HTTPError as e:
                if e.code == HTTP_UNAUTHORIZED_CODE:
                    self.zoom.update_token()
                    urlretrieve(f"{record.download_url}?access_token={self.zoom.access_token}", f"{title}.mp4")
                else:
                    raise e

            self.logger.info(f"{title}.mp4 downloaded")

        for index, record in enumerate(records):

            self.message_queue.put(Message(UPLOADING_RECORDS_STATUS, (index, len(records))))

            title = record.get_video_name()


            try:
                video = self.youtube.upload_video(
                    f"{title}.mp4",
                    title,
                    record.youtube_privacy_status)

                record.set_video(video)
                self.logger.info(f"{title}.mp4 published")
            except ResumableUploadError as e:
                if e.error_details[0]["reason"] == QUOTA_EXCEEDED_REASON:
                    self.message_queue.put(Message(QUOTA_EXCEEDED, end=True))
                    print("Quota exceeded")
                    break
                raise e

            if record.youtube_playlist_id is not None:

                # After video uploading and getting id video maybe still not available for using in next requests for
                # some time
                time.sleep(1)
                self.message_queue.put(Message(MOVE_TO_PLAYLIST_STATUS, (index, len(records))))
                self.youtube.move_video_to_playlist(record.video_id, record.youtube_playlist_id)

        for index, record in enumerate(records):
            if not record.save_flag:
                title = record.get_video_name()
                self.message_queue.put(Message(DELETING_FILES_STATUS, (index, len(records))))
                os.remove(f"{title}.mp4")

        self.message_queue.put(Message(END_STATUS, end=True))
