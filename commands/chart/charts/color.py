"""
Colored video titles over time
"""
from utils import charts


def _gen_data(conf, videos):
    x_tags, x_vals, x_colors = [], [], []

    for video in videos:
        video_id = video["id"]["videoId"]
        video_title = video["snippet"]["title"]
        video_date = video["snippet"]["publishedAt"]
        color = charts.pick_color(conf.title_colors, video_title)

        x_tags.append(f"{video_date} ({video_id})")
        x_vals.append(1)
        x_colors.append(color)

    # Return sorted results by tag
    return zip(*sorted(zip(x_tags, x_vals, x_colors)))


def _gen_chart(conf, x_tags, x_vals, x_colors):
    x_tags = charts.gen_spacing(x_tags, conf.tag_spacing)
    charts.gen_color_legend(conf.title_colors)
    return x_tags, x_vals, x_colors


def compute(conf, videos):
    charts.gen_bar_chart(conf, videos, _gen_data, _gen_chart)
