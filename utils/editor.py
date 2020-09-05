import moviepy.video.fx.all as vfx
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip


def add_info_overlay(clip, video, pos, counter, total):
    video_id = video["id"]["videoId"]
    video_title = video["snippet"]["title"]
    start, _, end = video["data"]["timestamps"][pos - 1]
    episode_counter = str(pos)
    aligned_counter = str(counter).rjust(len(str(total)))

    clip_text_title = (
        TextClip(
            txt=f"{video_title}\nhttps://youtube.com/watch?v={video_id}\nTime: {start}",
            fontsize=12,
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
            fontsize=12,
            color="black",
            bg_color="white",
            align="west",
        )
        .set_duration(clip.duration)
        .set_position(("left", "top"))
    )

    if clip.size != [1920, 1080]:
        clip = clip.fx(vfx.resize, width=1920)

    return CompositeVideoClip([clip, clip_text_title, clip_text_counter], size=(1920, 1080))
