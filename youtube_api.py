import datetime
import json
from urllib.request import urlopen

from helpers import data_file, str_to_sec, sec_to_str
from logger import Logger


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

    def _req(self, endpoint, max_results_count=10000, **kwargs):
        search_url = self._append_args(f"{self.api_url}/{endpoint}?", kwargs)

        results = []
        url = search_url
        while len(results) < max_results_count:
            raw_data = urlopen(url)
            data = json.load(raw_data)

            items = data["items"]
            results += items

            if len(items) == 0:
                Logger.info(f"No more items to retrieve")
                break

            Logger.info(f"Retrieved {len(items)} items. (total: {len(results)})")

            published_at = results[-1]["snippet"]["publishedAt"]
            # We remove one second to ensure we don't retrieve the same clip twice
            published_at = (
                datetime.datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%S%z")
                + datetime.timedelta(0, -1)
            ).strftime("%Y-%m-%dT%H:%M:%S%z").replace("+0000", "Z")

            url = f"{search_url}&publishedBefore={published_at}"

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


