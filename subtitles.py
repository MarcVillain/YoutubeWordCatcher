import difflib
import re


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
    if slice1[0] < slice2[0]:  # slice1 is leftmost
        return slice2[0] < slice1[2]  # slice2 ends before slice1 starts
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
            if str_a[i:i + splice_size] == str_b[j:j + splice_size]:
                return True

    return False


def clean_vtt(file):
    """
    Manually parsing since Youtube's vtt format is messed up
    """
    filtered = ""
    for line in file.readlines():
        tags = [
            r'</c>',
            r'<c(\.color\w+)?>',
        ]
        for pat in tags:
            line = re.sub(pat, '', line)
        if ">" in line:
            filtered += line

    content = ""
    for line in filtered.split("\n"):
        if "-->" in line:
            content += f"<{line[:12]}>"
        else:
            content += line

    return content

