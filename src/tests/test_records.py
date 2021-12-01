import json
from os import path

from src.zoom import ZoomClient


def get_data_path(filename):
    return path.join("data", filename)


def mock_repeat_get(dat_class, url):
    with open(get_data_path('application.json')) as f:
        return json.load(f)


def mock_response_get(url):
    return None


records = []


def get_templates_by_mask(record, date_required, index_required):
    record.date_required = date_required
    record.index_required = index_required

    return record.get_video_name()


class TestRecords:
    def test_get_records(self, mocker):
        mocker.patch('src.zoom.ZoomClient._repeat_get', mock_repeat_get)
        mocker.patch('requests.api.get', )

        client = ZoomClient("42", "secret")
        meetings = {1000000000000, 101010101010}
        global records
        records, is_completed = client.get_records(meetings)

        assert is_completed and len(records) == 2
        assert records[0].youtube_privacy_status == 'private'
        assert not records[0].save_flag
        assert records[0].index is not None and records[1].index is not None
        assert records[1].youtube_playlist_id is None

    def test_get_video_name(self):
        record = records[0]
        record.topic_template = "{topic} : {id}"
        record.index_template = " - {index}"
        record.date_template = " - {date}"

        assert get_templates_by_mask(record, False, False) == "MyTestPollMeeting : 1000000000000"
        assert get_templates_by_mask(record, True, False) == "MyTestPollMeeting : 1000000000000 - 29.08.19"
        assert get_templates_by_mask(record, False, True) == "MyTestPollMeeting : 1000000000000 - 1"
        assert get_templates_by_mask(record, True, True) == "MyTestPollMeeting : 1000000000000 - 29.08.19 - 1"
