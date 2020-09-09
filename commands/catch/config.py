import os

from utils.convert import str_to_bool


class CatchConfig:
    def __init__(self, **kwargs):
        """
        Initialize the configuration.
        :param kwargs: dictionary of key value to set
        """

        """
        General
        """
        # Name of the channel to extract the videos from
        self.channel_name = kwargs.get("channel_name", "")
        # Word to extract from the channel videos
        self.word_to_extract = kwargs.get("word_to_extract", "")
        # Final resolution of the video (smaller and bigger clips will be resized)
        self.resolution = kwargs.get("resolution", "1920x1080")

        """
        Youtube
        """
        # Your Youtube API key (https://developers.google.com/youtube/registering_an_application)
        self.api_key = kwargs.get("api_key", "")

        """
        Folders
        """
        # The folder where everything will be extracted
        self.output_folder = kwargs.get("output_folder", "")
        # The sub-folder used for persistent data storage (timestamps, lists, ...)
        self.data_folder = kwargs.get("data_folder", os.path.join(self.output_folder, "data"))
        # The sub-folder used for downloading files
        self.download_folder = kwargs.get("download_folder", os.path.join(self.output_folder, "download"))
        # The sub-folder used for the final video build
        self.build_folder = kwargs.get("build_folder", os.path.join(self.output_folder, "build"))

        """
        Clips settings
        """
        # Maximum length of a clip (in seconds)
        self.max_length = float(kwargs.get("max_length", 1.5))
        # Shift of the start timestamp of a clip (in seconds)
        self.start_shift = float(kwargs.get("start_shift", -0.25))
        # Shift of the end timestamp of a clip (in seconds)
        self.end_shift = float(kwargs.get("end_shift", 0.75))

        """
        Switches
        """
        # Should the program data be outputted?
        self.do_output_data = str_to_bool(kwargs.get("do_output_data", "True"))
        # Should the text overlay be applied?
        self.do_text_overlay = str_to_bool(kwargs.get("do_text_overlay", "True"))
        # Should the downloaded files be deleted?
        self.do_cleanup_downloads = str_to_bool(kwargs.get("do_cleanup_downloads", "True"))
        # Should the temporary clips files be deleted?
        self.do_cleanup_temporary_clips = str_to_bool(kwargs.get("do_cleanup_temporary_clips", "True"))
        # Should the video datas be computed even if they already exists?
        self.do_override_video_data = str_to_bool(kwargs.get("do_override_video_data", "False"))
        # Should the clips be generated even if they already exists?
        self.do_override_clips = str_to_bool(kwargs.get("do_override_clips", "False"))
        # Should the clips be generated?
        self.do_generate_clips = str_to_bool(kwargs.get("do_generate_clips", "True"))
        # Should the final video be generated?
        self.do_generate_final_video = str_to_bool(kwargs.get("do_generate_final_video", "True"))
        # Should the videos list data be updated?
        self.do_update_video_data = str_to_bool(kwargs.get("do_update_video_data", "False"))

        """
        Filters
        """
        # Only work with these video ids
        self.filter_videos_ids = kwargs.get("filter_videos_ids", [])
        # Ignore these video ids
        self.filter_out_videos_ids = kwargs.get("filter_out_videos_ids", [])

        """
        Thresholds
        """
        # Maximum amount of videos to download, cut and compose
        self.max_videos_amount = int(kwargs.get("max_videos_amount", 100000))
        # Maximum amount of threads to use when retrieving video data and cutting clips
        self.max_data_thread_workers = int(kwargs.get("max_data_thread_workers", 1))
        # Maximum amount of threads to use when wrinting a video clip to disk
        self.max_video_write_thread_workers = int(kwargs.get("max_video_write_thread_workers", 1))
        # Maximum number of files to open at once
        # This is useful when building the last clip as MoviePy creates a file
        # directory for every clip we open, so we have to do them by batches
        self.max_open_files = int(kwargs.get("max_open_files", 60))
