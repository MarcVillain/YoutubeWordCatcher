import html

import moviepy.video.fx.all as vfx
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip


def add_info_overlay(clip, size, video, pos, counter, total):
    video_id = video["id"]["videoId"]
    video_title = html.unescape(video["snippet"]["title"])
    video_published_at = video["snippet"]["publishedAt"]
    start, _, end = video["data"]["timestamps"][pos - 1]
    episode_counter = str(pos)
    aligned_counter = str(counter).rjust(len(str(total)))
    width, height = map(int, size.split("x"))

    clip_text_title = (
        TextClip(
            txt=f"{video_title}\nhttps://youtube.com/watch?v={video_id}\nTimestamp: {start}\nDate: {video_published_at}",
            fontsize=24,
            color="black",
            bg_color="white",
            align="west",
        )
        .set_duration(clip.duration)
        .set_position(("left", "bottom"))
    )
    clip_text_counter = (
        TextClip(
            txt=f"Episode counter: {episode_counter}\nTotal counter  : {aligned_counter}/{total}",
            fontsize=24,
            color="black",
            bg_color="white",
            align="west",
        )
        .set_duration(clip.duration)
        .set_position(("left", "top"))
    )

    if clip.size != [width, height]:
        clip = clip.fx(vfx.resize, width=width)

    return CompositeVideoClip([clip, clip_text_title, clip_text_counter], size=(width, height))
