from os.path import join

api_key = ""
channel_name = ""
word_to_extract = ""

max_clip_length = 1.5
start_clip_delay = -0.25
end_clip_delay = 0.75

build_dir = "/Users/Marc/Downloads/videos"
data_dir = join(build_dir, "data_save")

# If True, only retrieve videos data.
# If False, create the corresponding clip.
data_only = False

# Should we override existing clips and/or their data?
override_clips = False
override_clips_data = False

# Should downloaded files be removed?
cleanup_downloads = True

# Should we add video information on top of the clips?
# (titles, word counters, ...)
clips_overlay = True

# Should we concatenate all clips into one big video?
generate_final_clip = True

# List of video IDs to manipulate. If empty, all videos will be computed.
filter_video_ids = []
