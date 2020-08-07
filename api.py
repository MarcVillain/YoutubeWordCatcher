import json
from urllib.request import urlopen


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

    def search(self, **kwargs):
        return self._req("search", **kwargs)

    def captions(self, **kwargs):
        return self._req("captions", **kwargs)
