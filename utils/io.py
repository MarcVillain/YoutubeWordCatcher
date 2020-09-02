import os

import yaml


def load_yaml(file_path):
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        return yaml.load(f, Loader=yaml.BaseLoader)


def dump_yaml(file_path, data):
    folder_path = os.path.dirname(file_path)
    os.makedirs(folder_path, exist_ok=True)

    with open(file_path, "w") as f:
        yaml.dump(data)
