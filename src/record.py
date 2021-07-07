from datetime import datetime


class Record:

    def __init__(self, meeting, record):

        self.meeting_topic = meeting["topic"]
        self.meeting_id = meeting["id"]
        self.meeting_time = datetime.strptime(meeting["start_time"], "%Y-%m-%dT%H:%M:%SZ")
        self.download_url = record["download_url"]

        self.date_required = False
        self.index_required = False
        self.index = None
        self.video_id = None

    def get_video_name(self, topic_template, date_template, index_template):

        title = topic_template.format(
            topic=self.meeting_topic,
            id=self.meeting_id,
            date=self.meeting_time.strftime("%d.%m.%y")
        )

        if self.date_required:
            title += date_template.format(
                topic=self.meeting_topic,
                id=self.meeting_id,
                date=self.meeting_time.strftime("%d.%m.%y")
            )

        if self.index_required:
            title += index_template.format(
                topic=self.meeting_topic,
                id=self.meeting_id,
                date=self.meeting_time.strftime("%d.%m.%y"),
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
