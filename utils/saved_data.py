import os

from utils import logger, io


def write(conf, path, func):
    full_path = os.path.join(conf.data_folder, f"{path}.yaml")
    data = func()

    if not conf.do_output_data:
        return data

    logger.debug(f"Dump value of '{path}'", prefix=conf.logger_prefix)
    io.dump_yaml(full_path, data)
    return data


# Nice trick to be able to call the write function, even though
# we use a variable with the same name in the read function
def _write(conf, path, func):
    return write(conf, path, func)


def read(conf, path, func, write=True, update=False):
    full_path = os.path.join(conf.data_folder, f"{path}.yaml")

    if not update and os.path.exists(full_path):
        logger.debug(f"Load value of '{path}'", prefix=conf.logger_prefix)
        return io.load_yaml(full_path)

    if not write:
        return func()

    return _write(conf, path, func)


def read_videos(conf):
    videos = read(conf, "videos", lambda: [], write=False)
    max_videos_amount = min(conf.max_videos_amount, len(videos))
    videos = videos[:max_videos_amount]

    for i in range(max_videos_amount):
        video_id = videos[i]["id"]["videoId"]
        video_saved_data_path = os.path.join("videos", video_id)

        pos_log = str(i + 1).rjust(len(str(max_videos_amount)))
        conf.logger_prefix = f"({pos_log}/{max_videos_amount}) {video_id} >> "

        logger.info("Read saved video data", prefix=conf.logger_prefix)
        video_data = read(conf, video_saved_data_path, lambda: {}, write=False)
        videos[i]["data"] = video_data

    return videos
