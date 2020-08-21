import json
from urllib.request import urlopen

from helpers import data_file


class YoutubeAPI:
    """
    Wrapper around Youtube API v3
    """
    api_url = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key):
        self.api_key = api_key

    def _append_args(self, url, kwargs):
        url += f"key={self.api_key}"
        for k, v in kwargs.items():
            url += f"&{k}={v}"
        return url

    def _req(self, endpoint, max_results_count=500, **kwargs):
        search_url = self._append_args(f"{self.api_url}/{endpoint}?", kwargs)

        results = []
        url = search_url
        while len(results) < max_results_count:
            raw_data = urlopen(url)
            data = json.load(raw_data)

            results += data["items"]

            if "nextPageToken" not in data:
                break

            next_page_token = data["nextPageToken"]
            url = f"{search_url}&pageToken={next_page_token}"

        return results

    @data_file("Get channel ID", "channel_id")
    def get_channel_id(self, channel_name):
        search_results = self._req(
            "search",
            max_results_count=1,
            q=channel_name,
            part="snippet,id",
            type="channel",
            maxResults="1",
        )
        return search_results[0]["id"]["channelId"]

    @data_file("Get videos list", "videos")
    def get_videos(self, channel_id):
        search_results = self._req(
            "search",
            channelId=channel_id,
            part="snippet,id",
            type="video",
            order="date",
            maxResults="50",
        )

        data = []
        for search_item in search_results:
            if search_item["id"]["kind"] == "youtube#video":
                data.append(search_item)
        data.reverse()

        return data


