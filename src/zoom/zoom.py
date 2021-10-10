import base64
import requests

from .record import Record

ZOOM_OAUTH_AUTHORIZE = "https://zoom.us/oauth/authorize"
REDIRECT_URL = "http://localhost:7034/zoom"

RECORD_TYPE = "shared_screen_with_speaker_view"

TOKEN_EXPIRED_CODE = 124
RECORD_NOT_EXIST_CODE = 3301

COMPLETED_STATUS = "completed"


class RecordNotExistException(BaseException):
    pass


class ZoomClient:

    def _repeat_get(self, url):

        response = requests.get(url, headers={
            "Authorization": "Bearer" + self.access_token
        }).json()

        if response.get("code") == TOKEN_EXPIRED_CODE:
            self.update_token()
            response = requests.get(url, headers={
                "Authorization": "Bearer" + self.access_token
            }).json()

        return response

    def __init__(self, client_id, client_secret):

        self.client_id = client_id
        self.client_secret = client_secret
        self.base64_api = base64.b64encode((client_id + ":" + client_secret).encode()).decode()

        self.access_token = ""
        self.refresh_token = ""

    def use_cache(self, oauth2_cache):
        self.access_token = oauth2_cache["zoom_access_token"]
        self.refresh_token = oauth2_cache["zoom_refresh_token"]

    def get_authorize_code_url(self):

        return f"{ZOOM_OAUTH_AUTHORIZE}?response_type=code&" \
               f"client_id={self.client_id}&" \
               f"redirect_uri={REDIRECT_URL}"

    def login(self, code):

        response = requests.post("https://zoom.us/oauth/token", {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URL
        }, headers={
            "Authorization": "Basic " + self.base64_api
        }).json()

        self.access_token = response["access_token"]
        self.refresh_token = response["refresh_token"]

    def update_token(self):

        response = requests.post("https://zoom.us/oauth/token", {
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }, headers={
            "Authorization": "Basic " + self.base64_api
        }).json()

        self.access_token = response["access_token"]
        self.refresh_token = response["refresh_token"]

    def get_records(self, meetings):
        records = []
        is_completed = True

        first_iter = True
        next_page_token = ''

        meetings_count = dict.fromkeys(meetings, 0)

        while next_page_token or first_iter:
            first_iter = False

            response = self._repeat_get(
                f'https://api.zoom.us/v2/users/me/recordings?from=1970-01-01&next_page_token={next_page_token}'
            )

            for meeting in response["meetings"]:
                if meeting["id"] in meetings:

                    meetings_count[meeting["id"]] += 1

                    current_records = []
                    for file in meeting["recording_files"]:

                        if file["status"] != COMPLETED_STATUS:
                            is_completed = False
                            break

                        if file["recording_type"] == RECORD_TYPE:
                            current_records.append(Record(meeting, file))

                    if len(current_records) > 1:
                        for (index, record) in enumerate(current_records):
                            record.require_index(index+1)
                    records.extend(current_records)

            next_page_token = response.get("next_page_token")

            for record in records:
                if meetings_count[record.meeting_id] > 1:
                    record.require_date()

        return records, is_completed
