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
