import difflib
import re

from regex import regex

from utils import logger

"""
VTT Handling
"""


def _concat_str(str_a, str_b):
    i = 0
    while i < len(str_a):
        j = i
        k = 0
        while True:
            if j == len(str_a):
                return str_a[:i] + str_b
            if k == len(str_b):
                return str_a
            if str_a[j] != str_b[k]:
                break
            k += 1
            j += 1
        i += 1


def _do_words_overlap(slice1, slice2):
    # slice1 is leftmost
    if slice1[0] < slice2[0]:
        # slice2 ends before slice1 starts
        return slice2[0] < slice1[2]
    else:
        return slice1[0] < slice2[2]


def _match_str(str_a, str_b):
    curated_curr = str_a.replace(" ", "").replace("\n", "")
    curated_last = str_b.replace(" ", "").replace("\n", "")
    if curated_curr in curated_last or curated_last in curated_curr:
        return True

    diff_ratio = difflib.SequenceMatcher(a=str_a, b=str_b).ratio()
    if diff_ratio < 0.3:
        return True

    splice_size = 10
    for i in range(len(str_a) - splice_size + 1):
        for j in range(len(str_b) - splice_size + 1):
            if str_a[i : i + splice_size] == str_b[j : j + splice_size]:
                return True

    return False


def _clean_vtt(file):
    """
    Manually parsing since Youtube's vtt format is messed up
    """
    filtered = ""
    for line in file.readlines():
        tags = [
            r"</c>",
            r"<c(\.color\w+)?>",
        ]
        for pat in tags:
            line = re.sub(pat, "", line)
        if ">" in line:
            filtered += line

    content = ""
    for line in filtered.split("\n"):
        if "-->" in line:
            content += f"<{line[:12]}>"
        else:
            content += line

    return content


"""
Data extraction
"""


def _extract_timestamps(content, word_to_extract):
    logger.info(f"Extract timestamps where the word {word_to_extract} is pronounced")

    pattern = r"<(\d{2}:\d{2}:\d{2}.\d{3})>([^<]+)<(\d{2}:\d{2}:\d{2}.\d{3})>"
    return [match for match in regex.findall(pattern, content, overlapped=True) if word_to_extract in match[1]]


def _extract_time(content):
    # This is an approximation of the video length based on the last timestamp
    # TODO: Find a way to get the real video length
    #       without having to download the video clip
    logger.info("Extract time of the video")

    pattern = r"\d{2}:\d{2}:\d{2}.\d{3}"
    return [match for match in regex.findall(pattern, content, overlapped=True)][-1]


def extract_data(subtitles_file_path, word_to_extract):
    with open(subtitles_file_path, "r") as f:
        content = _clean_vtt(f)
        return {
            "timestamps": _extract_timestamps(content, word_to_extract),
            "time": _extract_time(content),
        }
