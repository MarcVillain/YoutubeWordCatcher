import datetime
import json
from urllib.request import urlopen

from utils import logger, io

api_url = "https://www.googleapis.com/youtube/v3"


def _req(api_key, endpoint, max_results_count=10000, **kwargs):
    search_url = f"{api_url}/{endpoint}?key={api_key}"
    # Append arguments to url
    for k, v in kwargs.items():
        search_url += f"&{k}={v}"

    # Retrieve list of results
    results = []
    url = search_url
    while len(results) < max_results_count:
        raw_data = urlopen(url)
        data = json.load(raw_data)

        items = data["items"]
        results += items

        if len(items) == 0:
            logger.info("No more items to retrieve")
            break

        logger.info(f"Retrieved {len(items)} items. (total: {len(results)})")

        published_at = results[-1]["snippet"]["publishedAt"]
        # We need to trim one second to ensure we
        # don't retrieve the same clip twice
        published_at = (
            (datetime.datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%S%z") + datetime.timedelta(0, -1))
            .strftime("%Y-%m-%dT%H:%M:%S%z")
            .replace("+0000", "Z")
        )

        url = f"{search_url}&publishedBefore={published_at}"

    return results


def get_channel_id(api_key, channel_name):
    search_results = _req(
        api_key,
        "search",
        max_results_count=1,
        q=channel_name,
        part="snippet,id",
        type="channel",
        maxResults="1",
    )
    return search_results[0]["id"]["channelId"]
