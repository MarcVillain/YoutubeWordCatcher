import os
from time import strftime, gmtime

from matplotlib import pyplot
from matplotlib.patches import Patch


def pick_color(colors, text):
    for sentence, color in colors.items():
        if sentence.lower() in text.lower():
            return color
    return "black"


def apply_spacing(values, spacing):
    # Fancy computing of spacing to choose
    spacing = int(len(values) / spacing)
    return [
        # Make appear first, last and modulo 0
        (tag if i == 0 or i == len(values) - 1 or i % spacing == 0 else None)
        for i, tag in enumerate(values)
    ]


def _filter_keep(filter_video_titles, string):
    return len(filter_video_titles) == 0 or any(
        [True for f in filter_video_titles if f.lower() in string.lower()]
    )


def generate_color_legend(colors):
    if len(colors) == 0:
        return

    patches = []
    for sentence, color in colors.items():
        patches.append(Patch(color=color, label=sentence))
    patches.append(Patch(color="black", label="Other"))

    pyplot.legend(handles=patches)


def plot_bar(x_vals, x_tags, x_colors):
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


def save(name, folder):
    current_datetime = strftime("%Y-%m-%d_%H:%M:%S", gmtime())
    chart_file_name = f"{name}_{current_datetime}.png"
    chart_file_path = os.path.join(folder, chart_file_name)
    os.makedirs(folder, exist_ok=True)
    pyplot.savefig(chart_file_path)
    return chart_file_path
