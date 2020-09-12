import os
import uuid
from collections import deque

from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from utils import logger, editor, saved_data, clips


def final_video(conf, videos):
    logger.info("Build final video")

    # Ensure build folder exists
    os.makedirs(conf.build_folder, exist_ok=True)

    # Define some useful variables
    max_videos_amount = min(conf.max_videos_amount, len(videos))
    videos = videos[:max_videos_amount]

    threshold = conf.max_open_files
    total_clips_count = sum(1 for _ in clips.list_for(conf, videos))

    conf.logger_prefix = "> "

    if total_clips_count == 0:
        logger.info("No clips to build")
        return None

    logger.debug(f"{total_clips_count} clips to build")

    video_clips_queue = deque(
        saved_data.read(
            conf,
            os.path.join("build", "video_clips_queue"),
            lambda: [clip_info for clip_info in clips.list_for(conf, videos)],
        )
    )
    temp_clips_queue = deque(saved_data.read(conf, os.path.join("build", "temp_clips_queue"), lambda: []))
    temp_clips_files_counter = saved_data.read(conf, os.path.join("build", "temp_clips_files_counter"), lambda: 1)

    # While there are clips to concatenate
    while len(video_clips_queue) > 0 or len(temp_clips_queue) > 2:
        video_clips = []
        is_line_ended = False
        do_concatenate_videos_clips = len(video_clips_queue) > 0

        if do_concatenate_videos_clips:
            # Create the group of videos to be concatenated
            clips_group = []
            while len(video_clips_queue) > 0 and len(clips_group) < threshold:
                clips_group.append(video_clips_queue.popleft())

            for i, (video, clip, pos, counter) in enumerate(clips_group):
                # Build video clip
                video_id = video["id"]["videoId"]
                clips_count_log = str(len(video.get("data", {}).get("clips", [])))
                pos_log = str(pos).rjust(len(clips_count_log))
                counter_log = str(counter).rjust(len(str(total_clips_count)))
                i_log = str(i + 1).rjust(len(str(threshold)))
                logger.info(
                    f"Build clip {pos_log}/{clips_count_log} of {video_id}",
                    prefix=f"[{counter_log}/{total_clips_count}|{i_log}/{threshold}] >> ",
                )
                video_clip = VideoFileClip(clip)
                if conf.do_text_overlay:
                    video_clip = editor.add_info_overlay(
                        video_clip, conf.resolution, video, pos, counter, total_clips_count
                    )

                # Add video clip to list
                video_clips.append(video_clip)

            # Check if we have a line of ordered temporary clips
            is_line_ended = len(video_clips_queue) == 0
        else:
            # Create the group of temporary clips videos to be concatenated
            clips_group = []
            while len(temp_clips_queue) > 0 and len(clips_group) < threshold:
                temp_clip = temp_clips_queue.popleft()
                # Prevent clips de-ordering
                if temp_clip is None:
                    if len(clips_group) == 1:
                        # Nothing to change or build really, just push pack the video file
                        temp_clips_queue.append(clips_group[0])
                        temp_clips_queue.append(None)
                        clips_group = []
                    else:
                        # We need to build the last temporary clip then insert a None
                        # to mark the end of the ordered temporary clips
                        is_line_ended = True
                    break

                clips_group.append(temp_clip)

            # Add video clips to list
            total_log = str(len(clips_group))
            for i, clip in enumerate(clips_group):
                pos_log = str(i + 1).rjust(len(total_log))
                logger.info(f"Load temporary clip '{os.path.basename(clip)}'", prefix=f"[{pos_log}/{total_log}] >> ")
                video_clips.append(VideoFileClip(clip))

        if len(video_clips) > 0:
            logger.info("Concatenate clips into a temporary clip")
            temp_clip = concatenate_videoclips(video_clips, method="compose")

            temp_clip_video_file_subpath = f"t{threshold}_c{temp_clips_files_counter}.mp4"
            temp_clip_video_file_path = os.path.join(conf.build_folder, temp_clip_video_file_subpath)
            temp_clip_audio_file_path = temp_clip_video_file_path.replace(".mp4", ".mp3")
            if os.path.exists(temp_clip_video_file_path) and not os.path.exists(temp_clip_audio_file_path):
                logger.info(f"Use existing temporary clip '{temp_clip_video_file_subpath}'")
            else:
                logger.info(f"Save temporary clip '{temp_clip_video_file_subpath}'")
                temp_clip.write_videofile(
                    temp_clip_video_file_path,
                    temp_audiofile=temp_clip_audio_file_path,
                    bitrate="20000k",
                    audio_bitrate="2000k",
                    threads=conf.max_video_write_thread_workers,
                )

            temp_clips_files_counter += 1

            # Add temporary clip to list
            temp_clips_queue.append(temp_clip_video_file_path)

            # Ensure we are marking the build loop to prevent de-ordering
            if is_line_ended:
                temp_clips_queue.append(None)

            # Close videos clips file descriptors
            for video_clip in video_clips:
                # MoviePy does not automatically close the CompositeVideoClip clips,
                # causing issues with a "too many file descriptors" error
                if isinstance(video_clip, CompositeVideoClip):
                    for c in video_clip.clips:
                        c.close()
                    if video_clip.bg is not None:
                        video_clip.bg.close()
                video_clip.close()

            # Cleanup temporary clips
            # (remove clips that got concatenated into another clip and are no longer needed)
            if not do_concatenate_videos_clips and conf.do_cleanup_temporary_clips:
                for video_clip in video_clips:
                    try:
                        logger.info(f"Remove temporary clip '{os.path.basename(video_clip.filename)}'")
                        os.remove(video_clip.filename)
                    except OSError as e:
                        logger.error(f"Unable to remove clip: {e}")

            # Save what happened in case something goes wrong to prevent having to start all over
            saved_data.write(conf, os.path.join("build", "video_clips_queue"), lambda: list(video_clips_queue))
            saved_data.write(conf, os.path.join("build", "temp_clips_queue"), lambda: list(temp_clips_queue))
            saved_data.write(conf, os.path.join("build", "temp_clips_files_counter"), lambda: temp_clips_files_counter)

    # Move final clip to desired result location
    last_temp_clip_file_path = temp_clips_queue[0] or temp_clips_queue[1]
    final_clip_file_path = os.path.join(conf.build_folder, f"{conf.channel_name}_{conf.word_to_extract}.mp4")

    while os.path.exists(final_clip_file_path):
        final_clip_file_path = f"{final_clip_file_path[:-4]}_{str(uuid.uuid4())[:6]}.mp4"

    try:
        os.rename(last_temp_clip_file_path, final_clip_file_path)
    except OSError as e:
        logger.error(f"Unable to rename temporary clip: {e}")
        return None

    return final_clip_file_path
