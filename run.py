import re

import difflib

import regex
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from api import YoutubeAPI
from local_values import LocalValue
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from pip._vendor import requests
from youtube_dl import YoutubeDL

if len(sys.argv) < 4:
    print("usage: ./run.py <api_key> <channel_name> <word>")
    exit(1)

api_key = sys.argv[1]
channel_name = sys.argv[2]
word_to_extract = sys.argv[3]

api = YoutubeAPI(api_key)


print("> Get channel ID")
search_results = api.search(
    max_results_count=1,
    q=channel_name,
    part="snippet,id",
    type="channel",
    maxResults="1",
)
channel_id = search_results[0]["id"]["channelId"]


print("> Get videos list")
search_results = api.search(
    channelId=channel_id,
    part="snippet,id",
    type="video",
    order="date",
    maxResults="50",
)

videos = []
for search_item in search_results:
    if search_item["id"]["kind"] == "youtube#video":
        videos.append(search_item)


def str_to_sec(timestamp):
    """
    format: HH:mm:ss.xxx
    """
    parts = re.split("[:.]", timestamp)
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2]) + (float(parts[3]) / 1000)


def sec_to_str(sec):
    """
    format: HH:mm:ss.xxx
    """
    hours = int(sec / 3600)
    sec %= 3600
    minutes = int(sec / 60)
    sec %= 60
    secs = int(sec / 1)
    sec %= 1
    millisecs = secs
    return f"{hours}:{minutes}:{secs}.{millisecs}"


def _concat_str(str_a, str_b):
    i = 0
    while i < len(str_a):
        j = i
        k = 0
        while True:
            if j == len(str_a):
                return str_a[:i] + str_b
            if k == len(str_b):
                return str_a
            if str_a[j] != str_b[k]:
                break
            k += 1
            j += 1
        i += 1


def _do_words_overlap(slice1, slice2):
    if slice1[0] < slice2[0]:  # slice1 is leftmost
        return slice2[0] < slice1[2]  # slice2 ends before slice1 starts
    else:
        return slice1[0] < slice2[2]


def _match_str(str_a, str_b):
    curated_curr = str_a.replace(" ", "").replace("\n", "")
    curated_last = str_b.replace(" ", "").replace("\n", "")
    if curated_curr in curated_last or curated_last in curated_curr:
        return True

    diff_ratio = difflib.SequenceMatcher(a=str_a, b=str_b).ratio()
    if diff_ratio < 0.3:
        return True

    splice_size = 10
    for i in range(len(str_a) - splice_size + 1):
        for j in range(len(str_b) - splice_size + 1):
            if str_a[i:i+splice_size] == str_b[j:j+splice_size]:
                return True

    return False


def _clean_vtt(file):
    """
    Manually parsing since Youtube's vtt format is messed up
    """
    filtered = ""
    for line in file.readlines():
        tags = [
            r'</c>',
            r'<c(\.color\w+)?>',
        ]
        for pat in tags:
            line = re.sub(pat, '', line)
        if ">" in line:
            filtered += line

    content = ""
    for line in filtered.split("\n"):
        if "-->" in line:
            content += f"<{line[:12]}>"
        else:
            content += line

    return content


print("> Process videos")
build_dir = "/Users/Marc/Downloads/videos"
cut_clips = []
for video in videos[:1]:
    video_id = video["id"]["videoId"]
    video_url = f"http://youtube.com/watch?v={video_id}"

    ydl_config = {
        "outtmpl": f"{build_dir}/{video_id}.mp4",
        "writesubtitles": True,
        "subtitleslangs": ["en"],
        "writeautomaticsub": True
    }
    print(f">> Download video {video_id}")
    with YoutubeDL(ydl_config) as ydl:
        ydl.download([video_url])

    print(f">> Extract timestamps where the word {word_to_extract} is pronounced")
    with open(f"{build_dir}/{video_id}.en.vtt", "r") as f:
        content = _clean_vtt(f)
        pattern = r"<(\d{2}:\d{2}:\d{2}.\d{3})>([^<]+)<(\d{2}:\d{2}:\d{2}.\d{3})>"
        timestamps = [match for match in regex.findall(pattern, content, overlapped=True) if word_to_extract in match[1]]

        print(">> Cut the clip")
        clips = []
        for start, _, end in timestamps:
            clips.append(VideoFileClip(f"{build_dir}/{video_id}.mp4").subclip(str_to_sec(start) - 0.15, str_to_sec(end) + 0.15))

        print(">> Concatenate the cuts")
        cut_clip = concatenate_videoclips(clips)
        cut_clip.write_videofile(f"{build_dir}/{video_id}_cut.mp4")
        cut_clips.append(VideoFileClip(f"{build_dir}/{video_id}_cut.mp4"))

print("> Concatenate the cut clips")
final_clip = concatenate_videoclips(cut_clips)
final_clip.write_videofile(f"{build_dir}/final.mp4")

