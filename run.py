import os
import re

import difflib
import sys

import regex
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from api import YoutubeAPI
from youtube_dl import YoutubeDL

if len(sys.argv) < 4:
    print("usage: ./run.py <api_key> <channel_name> <word>")
    exit(1)

api_key = sys.argv[1]
channel_name = sys.argv[2]
word_to_extract = sys.argv[3]

max_clip_length = 0.8
start_clip_delay = -0.25
end_clip_delay = 0.25

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
videos.reverse()


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


# Export data
with open("data.txt", "w") as f:
    f.write("ID,count")

print("> Process videos")
build_dir = "/Users/Marc/Downloads/videos"
cut_clips = []
total_counter = 0
for video in videos:
    video_id = video["id"]["videoId"]
    video_title = video["snippet"]["title"]
    video_url = f"http://youtube.com/watch?v={video_id}"

    video_path = f"{build_dir}/{video_id}.mp4"
    ydl_config = {
        "outtmpl": video_path,
        "writesubtitles": True,
        "subtitleslangs": ["en"],
        "writeautomaticsub": True
    }
    print(f"{video_id} >> Download video")
    with YoutubeDL(ydl_config) as ydl:
        ydl.download([video_url])

    subtitles_path = f"{build_dir}/{video_id}.en.vtt"
    if os.path.exists(subtitles_path):
        print(f"{video_id} >> Extract timestamps where the word {word_to_extract} is pronounced")
        with open(subtitles_path, "r") as f:
            content = _clean_vtt(f)
            pattern = r"<(\d{2}:\d{2}:\d{2}.\d{3})>([^<]+)<(\d{2}:\d{2}:\d{2}.\d{3})>"
            timestamps = [match for match in regex.findall(pattern, content, overlapped=True) if word_to_extract in match[1]]

        print(f"{video_id} >> Cut and compose the clips")
        clips = []
        episode_counter = 0
        for start, _, end in timestamps:
            episode_counter += 1
            total_counter += 1

            video_start = str_to_sec(start) + start_clip_delay
            video_end = str_to_sec(end) + end_clip_delay
            # Prevent clip from being too long
            if video_end - video_start > max_clip_length:
                video_end = video_start + max_clip_length
            clip_video = VideoFileClip(f"{build_dir}/{video_id}.mp4").subclip(video_start, video_end)
            clip_text_title = TextClip(
                txt=f"{video_title}\nhttps://youtube.com/watch?v={video_id}\nTime: {start}",
                fontsize=30,
                color="black",
                bg_color="white",
                align="west",
            ).set_duration(clip_video.duration).set_position(("left", "bottom"))
            clip_text_counter = TextClip(
                txt=f"Episode counter: {episode_counter}\nTotal counter  : {total_counter}",
                fontsize=30,
                color="black",
                bg_color="white",
                align="west",
            ).set_duration(clip_video.duration).set_position(("left", "top"))
            clip_comp = CompositeVideoClip([clip_video, clip_text_title, clip_text_counter])
            clips.append(clip_comp)

        # Export data
        with open("data.txt", "a") as f:
            f.write(f"{video_id},{episode_counter}")

        print(f"{video_id} >> Concatenate the cuts")
        cut_clip_path = f"{build_dir}/clips/{video_id}.mp4"
        cut_clip = concatenate_videoclips(clips)
        cut_clip.write_videofile(cut_clip_path)
        cut_clip_video = VideoFileClip(cut_clip_path)
        cut_clips.append(cut_clip_video)
    else:
        print(f"{video_id} >> No subtitles for video")

    print(f"{video_id} >> Remove unnecessary files")
    try:
        os.remove(video_path)
    except OSError:
        pass
    try:
        os.remove(subtitles_path)
    except OSError:
        pass

print("> Concatenate all the clips")
final_clip_path = f"{build_dir}/{word_to_extract}_{channel_name}.mp4"
final_clip = concatenate_videoclips(cut_clips)
final_clip.write_videofile(final_clip_path)
