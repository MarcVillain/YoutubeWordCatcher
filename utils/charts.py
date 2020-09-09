import colorsys
import os
from time import strftime, gmtime

from matplotlib import pyplot
from matplotlib.patches import Patch
from pandas import np

from utils import logger


def pick_color(colors, text):
    for sentence, color in colors.items():
        if sentence.lower() in text.lower():
            return color
    return "black"


def gen_unique_colors(num_colors):
    # https://stackoverflow.com/questions/470690/how-to-automatically-generate-n-distinct-colors
    # Response by Uri Cohen:
    colors = []
    for i in np.arange(0., 360., 360. / num_colors):
        hue = i/360.
        lightness = (50 + np.random.rand() * 10)/100.
        saturation = (90 + np.random.rand() * 10)/100.
        colors.append(colorsys.hls_to_rgb(hue, lightness, saturation))
    return colors


def gen_spacing(values, spacing):
    # Fancy computing of spacing to choose
    spacing = int(len(values) / spacing)
    return [
        # Make appear first, last and modulo 0
        (tag if i == 0 or i == len(values) - 1 or i % spacing == 0 else None)
        for i, tag in enumerate(values)
    ]


def gen_color_legend(colors):
    if len(colors) == 0:
        return

    patches = []
    for sentence, color in colors.items():
        patches.append(Patch(color=color, label=sentence))
    patches.append(Patch(color="black", label="Other"))

    pyplot.legend(handles=patches)


def _plot_bar(x_tags, x_vals, x_colors):
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


def gen_bar_chart(conf, videos, data_func, chart_func=None):
    logger.info("Compute the data")
    x_tags, x_vals, x_colors = data_func(conf, videos)

    logger.info("Build the chart")
    if chart_func is not None:
        x_tags, x_vals, x_colors = chart_func(conf, x_tags, x_vals, x_colors)
    _plot_bar(x_tags, x_vals, x_colors)

    # Export the chart
    if conf.do_output_file:
        chart_file_path = _save(f"{conf.channel_name}_amount_of_{conf.word_to_extract}_", conf.charts_folder)
        logger.info(f"Chart saved at: {chart_file_path}")

    # Display the chart
    if conf.do_display_chart:
        logger.info("Display the chart")
        pyplot.show()
