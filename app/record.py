import os
from datetime import datetime


class Record:

    def __init__(self, meeting, record):
        self.strftime_template = "%d.%m.%y %H:%M"

        self.meeting_topic = meeting["topic"]
        self.meeting_id = meeting["id"]
        self.meeting_time = datetime.strptime(meeting["start_time"], "%Y-%m-%dT%H:%M:%SZ")
        self.download_url = record["download_url"]

        self.date_required = False
        self.index_required = False
        self.index = None
        self.video_id = None

        self.topic_template = None
        self.date_template = None
        self.index_template = None

        self.save_flag = False
        self.youtube_privacy_status = 'private'

        self.youtube_playlist_id = None

    @staticmethod
    def _get_template(template, environ_key):
        return template if template is not None else os.environ[environ_key]

    def get_video_name(self):

        title = self._get_template(self.topic_template, 'TOPIC_TEMPLATE').format(
            topic=self.meeting_topic,
            id=self.meeting_id,
            date=self.meeting_time.strftime(self.strftime_template)
        )

        if self.date_required:
            title += self._get_template(self.date_template, 'DATE_TEMPLATE').format(
                topic=self.meeting_topic,
                id=self.meeting_id,
                date=self.meeting_time.strftime(self.strftime_template)
            )

        if self.index_required:
            title += self._get_template(self.index_template, 'INDEX_TEMPLATE').format(
                topic=self.meeting_topic,
                id=self.meeting_id,
                date=self.meeting_time.strftime(self.strftime_template),
                index=self.index
            )

        return title

    def require_index(self, index):

        self.index_required = True
        self.index = index

    def require_date(self):

        self.date_required = True

    def set_video(self, video):

        self.video_id = video["id"]
