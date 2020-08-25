import os
import re

from matplotlib.patches import Patch

import config
import matplotlib.pyplot as plt
import yaml

from helpers import str_to_sec

videos_infos = {}
videos_info_path = os.path.join(config.data_dir, "videos.yaml")
with open(videos_info_path, "r") as f:
    videos_info = yaml.load(f, Loader=yaml.FullLoader)
    for video in videos_info:
        video_id = video["id"]["videoId"]
        videos_infos[video_id] = video

# key = string to look for in title, value = the color
# example: {"Test" : "red"} will set to red every video that contains "Test" (case insensitive)
colors = {
}
# Filter out titles that contains any of the string in the list
video_title_filter = []


def filter_keep(string):
    return len(video_title_filter) == 0 or any([True for f in video_title_filter if f.lower() in string.lower()])


x_tags = []
x_vals = []
x_colors = []
for filename in os.listdir(config.data_dir):
    filepath = os.path.join(config.data_dir, filename)
    if os.path.isfile(filepath) and re.match(r"[a-zA-Z0-9-_]{11}.yaml", filename):
        with open(filepath, "r") as f:
            file_data = yaml.load(f, Loader=yaml.FullLoader)
            file_data = file_data or {}

            video_id = filename.split(".")[0]
            video_info = videos_infos[video_id]
            video_date = video_info["snippet"]["publishedAt"]
            video_title = video_info["snippet"]["title"]

            count = len(file_data.get("timestamps", []))
            video_time = 0  # In seconds
            last_timestamp_time = file_data.get("time", None)
            if last_timestamp_time is not None:
                video_time = str_to_sec(last_timestamp_time)

            if filter_keep(video_title):
                x_tags.append(f"{video_date} ({video_id})")
                # Ensure all columns are visible
                x_vals.append(count / video_time if video_time != 0 else 0.0004)

                found = False
                for sentence, color in colors.items():
                    if sentence.lower() in video_title.lower():
                        x_colors.append(color)
                        found = True
                        break

                if not found:
                    x_colors.append("blue")

# Sort the lists
x_tags, x_vals, x_colors = zip(*sorted(zip(x_tags, x_vals, x_colors)))

# Add spacing between tags (remove to get every value)
spacing = int(len(x_tags) / 20) or 1
spacing = 1
x_tags = [
    (tag if i == 0 or i == len(x_tags) - 1 or i % spacing == 0 else None)
    for i, tag in enumerate(x_tags)
]

# Build colored legend
patches = []
for sentence, color in colors.items():
    if filter_keep(sentence):
        patches.append(Patch(color=color, label=sentence))
if filter_keep("Other"):
    patches.append(Patch(color="blue", label="Other"))
plt.legend(handles=patches)

# data = {k: v for k, v in data.items() if v != 0}

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
plt.bar(range(len(x_vals)), x_vals, align="center", color=x_colors)

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
plt.xticks(range(len(x_tags)), x_tags, rotation="vertical")

# You could export this to a file using plt.savefig("chart.png")
plt.show()
