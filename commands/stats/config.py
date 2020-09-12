from commands.config import AllConfig


class StatsConfig(AllConfig):
    def __init__(self, **kwargs):
        """
        Initialize the configuration.
        :param kwargs: dictionary of key value to set
        """
        super().__init__(**kwargs)
