from configparser import ConfigParser


def read(file, section, config_class):
    parser = ConfigParser()
    parser.read(file)

    args = {}
    for s in parser.sections():
        if s in ["all", section]:
            for key in parser[s]:
                args[key] = parser[s][key]

    config = config_class(**args)

    return config
