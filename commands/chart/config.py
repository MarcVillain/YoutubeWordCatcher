import ast
import os

from utils.convert import str_to_bool


class ChartConfig:
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

        """
        Options
        """
        # Dictionary of title keys associated with color values
        # example: {"[TAG]": "red"}
        self.title_colors = dict(ast.literal_eval(kwargs.get("title_colors", "{}")))

        """
        Words chart options
        """
        # If set, all words are black except for the given ones. Else, give random color to every word.
        self.words_chart_words_color = dict(ast.literal_eval(kwargs.get("words_chart_words_color", "{}")))
        # Maximum number of words to display on the chart (only get n first)
        self.words_chart_max_words_display_count = int(kwargs.get("words_chart_max_words_display_count", 500))

        """
        Folders
        """
        # The folder where everything was extracted
        self.output_folder = kwargs.get("output_folder", "")
        # The sub-folder used for persistent data storage (timestamps, lists, ...)
        self.data_folder = kwargs.get("data_folder", os.path.join(self.output_folder, "data"))
        # The sub-folder used to save charts
        self.charts_folder = kwargs.get("charts_folder", os.path.join(self.output_folder, ""))

        """
        Switches
        """
        # Should an output file be created?
        self.do_output_file = str_to_bool(kwargs.get("do_output_file", "False"))
        # Should the chart be displayed on screen?
        self.do_display_chart = str_to_bool(kwargs.get("do_display_chart", "True"))

        """
        Filters
        """
        # Only work with these video ids
        self.filter_videos_ids = kwargs.get("filter_videos_ids", [])
        # Only work with these video titles
        self.filter_videos_titles = kwargs.get("filter_videos_titles", [])

        """
        Thresholds
        """
        # Maximum amount of videos to download, cut and compose
        self.max_videos_amount = int(kwargs.get("max_videos_amount", 100000))
        # Above the specified 'n' spacing, make the tags appear every so often
        # example: 40 elements with a space of 20 will have a tag appear every one in two.
        self.tag_spacing = int(kwargs.get("tag_spacing", 20))
