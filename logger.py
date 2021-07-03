from logging import Logger, StreamHandler, DEBUG, Formatter


class ScopeLogger:
    def __init__(self, logger: Logger, title: str) -> None:
        self.logger = logger
        self.title = title

    def __enter__(self):
        self.logger.debug(f'--- start {self.title} ---')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.debug(f'--- end {self.title} ---')


class CustomLogger(Logger):
    def __init__(self, name: str) -> None:
        super().__init__(name)

        handler = StreamHandler()
        formatter = Formatter(
            '- %(pathname)s, line %(lineno)d, in %(funcName)s \n'
            '  - %(threadName)s: [%(levelname)s] %(message)s')

        handler.setFormatter(formatter)

        handler.setLevel(DEBUG)
        self.setLevel(DEBUG)

        self.addHandler(handler)

        self.propagate = False

    def scope(self, title: str) -> ScopeLogger:
        return ScopeLogger(self, title)


def init_logger(name: str):
    logger = CustomLogger(name)
    logger.warning('init_logger is deplicate !')
    logger.warning('use CustomLogger')

    return logger
