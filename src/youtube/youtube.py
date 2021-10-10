import time
import random

import googleapiclient.discovery
import requests
import google.oauth2.credentials
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

YOUTUBE_OAUTH_AUTHORIZE = "https://accounts.google.com/o/oauth2/v2/auth"
YOUTUBE_OAUTH_TOKEN = "https://oauth2.googleapis.com/token"

YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"

REDIRECT_URL = "http://localhost:7034/youtube"

TOKEN_EXPIRED_CODE = 401

MAX_RETRIES = 10
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


class TokenExpiredException(BaseException):
    pass


class YoutubeClient:

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

        self.access_token = ""
        self.refresh_token = ""

        self.client = None

    def _repeat_request(self, request):

        try:
            response = request(self.client).execute()
        except RefreshError:
            self.update_token()
            response = request(self.client).execute()

        return response

    def get_authorize_code_url(self):
        return f"{YOUTUBE_OAUTH_AUTHORIZE}?scope={YOUTUBE_SCOPE}&" \
               f"access_type=offline&" \
               f"response_type=code&" \
               f"client_id={self.client_id}&" \
               f"redirect_uri={REDIRECT_URL}"

    def use_cache(self, oauth2_cache):
        self.access_token = oauth2_cache["youtube_access_token"]
        self.refresh_token = oauth2_cache["youtube_refresh_token"]
        self.build_client()

    def build_client(self):
        credentials = google.oauth2.credentials.Credentials(
            self.access_token
        )
        self.client = googleapiclient.discovery.build(
            "youtube", "v3", credentials=credentials)

    def login(self, code):
        response = requests.post(YOUTUBE_OAUTH_TOKEN, {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URL
        }).json()

        self.access_token = response["access_token"]
        self.refresh_token = response["refresh_token"]
        self.build_client()

    def upload_video(self, file, title, privacy):

        body = {
            "snippet": {
                "title": title,
                "description": "Video uploaded with Zoom Video Publisher",
            },

            "status": {
                "privacyStatus": privacy
            }
        }

        def insert_request(client):
            return client.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=MediaFileUpload(file, chunksize=-1, resumable=True)
            )

        try:
            response = self.resumable_upload(insert_request(self.client))
        except RefreshError:
            self.update_token()
            response = self.resumable_upload(insert_request(self.client))

        return response

    def resumable_upload(self, insert_request):

        response = None
        error = None
        retry = 0

        while response is None:
            try:
                print("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print(f"Video id '{response['id']}' was successfully uploaded.")
                    else:
                        exit("The upload failed with an unexpected response: %s" % response)
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
                else:
                    raise

            if error is not None:
                print(error)
                retry += 1
                if retry > MAX_RETRIES:
                    exit("No longer attempting to retry.")

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print(f"Sleeping {sleep_seconds} seconds and then retrying...")
                time.sleep(sleep_seconds)

        return response

    def move_video_to_playlist(self, video_id, playlist_id):

        def request(client):
            return client.playlistItems().insert(part="snippet", body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            })

        response = self._repeat_request(request)
        return response

    def update_token(self):
        response = requests.post("https://oauth2.googleapis.com/token", {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }).json()

        self.access_token = response["access_token"]
        self.build_client()
