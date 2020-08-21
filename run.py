import sys

from moviepy.video.compositing.concatenate import concatenate_videoclips

import config

from logger import Logger
from video_clip import VideoClip
from youtube_api import YoutubeAPI

if len(sys.argv) < 4:
    print("usage: ./run.py <api_key> <channel_name> <word>")
    exit(1)

config.api_key = sys.argv[1]
config.channel_name = sys.argv[2]
config.word_to_extract = sys.argv[3]

api = YoutubeAPI(config.api_key)
channel_id = api.get_channel_id(config.channel_name)
videos = api.get_videos(channel_id)

Logger.info("Process videos")
cut_clips = []
tot_vid = len(videos)
for i, video in enumerate(videos):
    pos_vid = str(i + 1).rjust(len(str(tot_vid)))
    Logger.level += 1
    Logger.pre = f"({pos_vid}/{tot_vid})"

    with VideoClip(video, config.build_dir, config.word_to_extract, subtitles_only=config.data_only) as video_clip:
        if video_clip:
            cut_clips.append(video_clip)

    Logger.level -= 1
    Logger.pre = ""

if len(cut_clips) > 0:
    Logger.info("Concatenate all the clips")
    final_clip_path = f"{config.build_dir}/{config.word_to_extract}_{config.channel_name}.mp4"
    final_clip = concatenate_videoclips(cut_clips)
    final_clip.write_videofile(final_clip_path)
else:
    Logger.info("No clip to concatenate")
