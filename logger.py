from logging import getLogger, StreamHandler, DEBUG, Formatter


def init_logger(name: str):
    logger = getLogger(name)

    handler = StreamHandler()
    formatter = Formatter(
        '- %(pathname)s, line %(lineno)d, in %(funcName)s \n'
        '  - %(threadName)s: [%(levelname)s] %(message)s')

    handler.setFormatter(formatter)

    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)

    logger.addHandler(handler)

    logger.propagate = False

    return logger
