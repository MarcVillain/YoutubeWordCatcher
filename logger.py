class Logger:
    pre = ""
    level = 1

    @classmethod
    def info(cls, msg):
        if cls.pre:
            print(cls.pre, end=" ")
        print(">" * cls.level, msg)

    @classmethod
    def error(cls, msg):
        cls.info(msg)
