import os
from time import strftime, gmtime

from matplotlib import pyplot
from matplotlib.patches import Patch

from utils import logger


def pick_color(colors, text):
    for sentence, color in colors.items():
        if sentence.lower() in text.lower():
            return color
    return "black"


def _apply_spacing(values, spacing):
    # Fancy computing of spacing to choose
    spacing = int(len(values) / spacing)
    return [
        # Make appear first, last and modulo 0
        (tag if i == 0 or i == len(values) - 1 or i % spacing == 0 else None)
        for i, tag in enumerate(values)
    ]


def _filter_keep(filter_video_titles, string):
    return len(filter_video_titles) == 0 or any([True for f in filter_video_titles if f.lower() in string.lower()])


def _generate_color_legend(colors):
    if len(colors) == 0:
        return

    patches = []
    for sentence, color in colors.items():
        patches.append(Patch(color=color, label=sentence))
    patches.append(Patch(color="black", label="Other"))

    pyplot.legend(handles=patches)


def _plot_bar(x_vals, x_tags, x_colors):
    """
    bar(...) => Plot the values

    x_vals = [2, 3]

    . -|
    3 -|     x
    2 -|  x
    1 -|
    0 -+--|--|--|
          0  1  .
    """
    pyplot.bar(range(len(x_vals)), x_vals, align="center", color=x_colors)

    """
        xticks(...) => Name the values

        x_tags = ["a", "b"]

        . -|
        3 -|     x
        2 -|  x
        1 -|
        0 -+--|--|--|
              a  b  .
    """
    pyplot.xticks(range(len(x_tags)), x_tags, rotation="vertical")


def _save(name, folder):
    current_datetime = strftime("%Y-%m-%d_%H:%M:%S", gmtime())
    chart_file_name = f"{name}_{current_datetime}.png"
    chart_file_path = os.path.join(folder, chart_file_name)
    os.makedirs(folder, exist_ok=True)
    pyplot.savefig(chart_file_path)
    return chart_file_path


def gen_bar_chart(conf, videos, data_func):
    logger.info("Compute the data")
    x_tags, x_vals, x_colors = data_func(conf, videos)

    logger.info("Build the chart")
    x_tags = _apply_spacing(x_tags, conf.tag_spacing)
    _generate_color_legend(conf.title_colors)
    _plot_bar(x_vals, x_tags, x_colors)

    # Export the chart
    if conf.do_output_file:
        chart_file_path = _save(f"{conf.channel_name}_amount_of_{conf.word_to_extract}_", conf.charts_folder)
        logger.info(f"Chart saved at: {chart_file_path}")

    # Display the chart
    if conf.do_display_chart:
        logger.info("Display the chart")
        pyplot.show()
