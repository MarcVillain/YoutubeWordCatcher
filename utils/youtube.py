import datetime
import json
import os
from urllib.request import urlopen

from youtube_dl import YoutubeDL, DownloadError

from utils import logger

"""
Youtube API
"""

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


def get_videos(api_key, channel_id):
    search_results = _req(
        api_key,
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


"""
Youtube DL
"""


def download(video_id, output_path, subtitles=True, video=True):
    video_file_path = os.path.join(output_path, f"{video_id}.mp4")
    ydl_config = {
        "outtmpl": video_file_path,
    }

    if subtitles:
        ydl_config["writesubtitles"] = True
        ydl_config["subtitleslangs"] = ["en"]
        ydl_config["writeautomaticsub"] = True

    if not video:
        ydl_config["skip_download"] = True

    video_url = f"http://youtube.com/watch?v={video_id}"
    with YoutubeDL(ydl_config) as ydl:
        try:
            ydl.download([video_url])
        except DownloadError as e:
            logger.error(f"Unable to download: {e}")
            return None, None

    subtitles_file_path = os.path.join(output_path, f"{video_id}.en.vtt")
    return subtitles_file_path, video_file_path
