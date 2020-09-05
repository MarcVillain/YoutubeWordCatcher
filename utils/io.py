import os

import yaml


def load_yaml(file_path):
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def dump_yaml(file_path, data):
    folder_path = os.path.dirname(file_path)
    os.makedirs(folder_path, exist_ok=True)

    # TODO: If file already exists, dump aside then move
    #       to prevent data loss (example: when using ctrl+c)
    with open(file_path, "w") as f:
        f.write(yaml.dump(data))
