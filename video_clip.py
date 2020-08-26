import os

from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from regex import regex
from youtube_dl import YoutubeDL, DownloadError

import config
import subtitles
from helpers import data_file, str_to_sec
from logger import Logger


class VideoClip:
    total_word_counter = 0

    def __init__(self, info, dest_folder, word_to_extract, subtitles_only=False):
        self.id = info["id"]["videoId"]
        Logger.pre += f" {self.id}"
        self.title = info["snippet"]["title"]

        self.dest_folder = dest_folder
        self.word_to_extract = word_to_extract
        self.subtitles_only = subtitles_only

        self.video_file_path = os.path.join(dest_folder, f"{self.id}.mp4")
        self.cut_clip_path = os.path.join(dest_folder, "clips", f"{self.id}.mp4")
        self.subtitles_path = os.path.join(dest_folder, f"{self.id}.en.vtt")
        self.subtitles_fd = None
        self.timestamps = None

    def _download_video(self, with_subtitles=True, subtitles_only=False):
        ydl_config = {
            "outtmpl": self.video_file_path,
        }

        if with_subtitles:
            ydl_config["writesubtitles"] = True
            ydl_config["subtitleslangs"] = ["en"]
            ydl_config["writeautomaticsub"] = True

        if subtitles_only:
            ydl_config["skip_download"] = True

        Logger.info("Download files")

        video_url = f"http://youtube.com/watch?v={self.id}"
        with YoutubeDL(ydl_config) as ydl:
            try:
                ydl.download([video_url])
            except DownloadError as e:
                Logger.error(f"Unable to download file: {e}")
                return False

        return True

    def _cut_and_compose(self):
        Logger.info("Cut and compose the clips")
        clips = []
        episode_word_counter = 0
        for start, _, end in self.timestamps:
            episode_word_counter += 1
            VideoClip.total_word_counter += 1

            video_start = str_to_sec(start) + config.start_clip_delay
            video_end = str_to_sec(end) + config.end_clip_delay
            # Prevent clip from being too long
            if video_end - video_start > config.max_clip_length:
                video_end = video_start + config.max_clip_length
            clip_video = VideoFileClip(self.video_file_path).subclip(video_start, video_end)
            if config.clips_overlay:
                clip_text_title = TextClip(
                    txt=f"{self.title}\nhttps://youtube.com/watch?v={self.id}\nTime: {start}",
                    fontsize=12,
                    color="black",
                    bg_color="white",
                    align="west",
                ).set_duration(clip_video.duration).set_position(("left", "bottom"))
                clip_text_counter = TextClip(
                    txt=f"Episode counter: {episode_word_counter}\nTotal counter  : {VideoClip.total_word_counter}",
                    fontsize=12,
                    color="black",
                    bg_color="white",
                    align="west",
                ).set_duration(clip_video.duration).set_position(("left", "top"))
                clip_comp = CompositeVideoClip([clip_video, clip_text_title, clip_text_counter])
                clips.append(clip_comp)
            else:
                clips.append(clip_video)

        if len(self.timestamps) > 0:
            Logger.info("Concatenate the cuts")
            try:
                # Ensure destination folder exists
                os.makedirs(os.path.dirname(self.cut_clip_path), exist_ok=True)

                # Delete pre-existing file if there
                # (accessing this line of code mean the file
                # was not there in the first place)
                try:
                    os.remove(self.cut_clip_path)
                except OSError:
                    pass

                # Create the cut clip
                cut_clip = concatenate_videoclips(clips)
                cut_clip.write_videofile(self.cut_clip_path)
                cut_clip_video = VideoFileClip(self.cut_clip_path)
                return cut_clip_video
            except OSError as e:
                Logger.error(f"Something went wrong: {e}")

        return None

    def __enter__(self):
        if len(config.filter_video_ids) > 0 and self.id not in config.filter_video_ids:
            return None

        # Check if clip already exists
        if os.path.exists(self.cut_clip_path):
            if not config.override_clips:
                Logger.info("Video clip already created")
                cut_clip_video = VideoFileClip(self.cut_clip_path)
                data = data_file("Retrieve video data", self.id)(lambda: {})()
                VideoClip.total_word_counter += len(data["timestamps"])
                return cut_clip_video
            else:
                Logger.info("Video clip already created (will be overridden)")

        # Retrieve video data or generate it
        @data_file("Retrieve video data", self.id, config.override_clips_data)
        def _retrieve_video_data():
            data = {}

            if not self._download_video(subtitles_only=True):
                return None

            if os.path.exists(self.subtitles_path):
                self.subtitles_fd = open(self.subtitles_path, "r")

                Logger.info(f"Extract timestamps where the word {self.word_to_extract} is pronounced")
                content = subtitles.clean_vtt(self.subtitles_fd)

                pattern = r"<(\d{2}:\d{2}:\d{2}.\d{3})>([^<]+)<(\d{2}:\d{2}:\d{2}.\d{3})>"
                data["timestamps"] = [match for match in regex.findall(pattern, content, overlapped=True) if
                                      self.word_to_extract in match[1]]

                # This is an approximation of the video length based on the last timestamp
                # TODO: Find a way to get the real video length
                #       without having to download the video clip
                pattern = r"\d{2}:\d{2}:\d{2}.\d{3}"
                data["time"] = [match for match in regex.findall(pattern, content, overlapped=True)][-1]
            else:
                data["timestamps"] = []
                Logger.info("No subtitles for video")

            return data

        video_data = _retrieve_video_data()
        self.timestamps = video_data.get("timestamps", None)

        if (
            len(self.timestamps) > 0
            and not self.subtitles_only
            and self._download_video(with_subtitles=False)
        ):
            return self._cut_and_compose()
        else:
            Logger.info("Not creating clip because word not appearing")

        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.subtitles_fd is not None:
            self.subtitles_fd.close()

        if config.cleanup_downloads:
            if os.path.exists(self.subtitles_path):
                try:
                    Logger.info("Remove subtitles file")
                    os.remove(self.subtitles_path)
                except OSError:
                    pass

            if os.path.exists(self.video_file_path):
                try:
                    Logger.info("Remove video file")
                    os.remove(self.video_file_path)
                except OSError:
                    pass

            if os.path.exists(f"{self.video_file_path}.part"):
                try:
                    Logger.info("Remove incomplete video file")
                    os.remove(f"{self.video_file_path}.part")
                except OSError:
                    pass
