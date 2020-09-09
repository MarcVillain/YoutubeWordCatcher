"""
Frequence of apparition of each matched word
"""
from utils import charts


def _gen_data(conf, videos):
    # Generate data
    all_words_count = 0
    amount_dict = {}
    for video in videos:
        for _, word, _ in video.get("data", {}).get("timestamps", []):
            all_words_count += 1
            word = word.strip().lower()
            amount_dict[word] = amount_dict.get(word, 0) + 1

    # Sort from low amount to high amount
    amount_list = sorted([(amount, word) for word, amount in amount_dict.items()])

    # Get only part of the dataset
    amount_list = amount_list[-conf.words_chart_max_words_display_count :]

    # Plot data
    x_tags, x_vals = [], []
    displayed_words_count = len(amount_list)
    for i, (amount, word) in enumerate(amount_list):
        pos = displayed_words_count - i
        freq = amount / all_words_count
        freq_str = str(int(freq * 100000) / 100000.0)
        x_tags.append(f"(amount:{amount} freq:{freq_str} pos:{pos}) {word}")
        x_vals.append(freq)

    # Generate colors
    if len(conf.words_chart_words_color.keys()) > 0:
        x_colors = ["black"] * len(amount_list)
        for word, color in conf.words_chart_words_color.items():
            amount_val = (amount_dict[word], word)
            if amount_val in amount_list:
                word_index = amount_list.index(amount_val)
                x_colors[word_index] = color
    else:
        x_colors = charts.gen_unique_colors(len(amount_list))

    return x_tags, x_vals, x_colors


def _gen_chart(conf, x_tags, x_vals, x_colors):
    if len(conf.words_chart_words_color.keys()) > 0:
        charts.gen_color_legend(conf.words_chart_words_color)
    return x_tags, x_vals, x_colors


def compute(conf, videos):
    charts.gen_bar_chart(conf, videos, _gen_data, _gen_chart)
