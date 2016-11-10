import logging


class Handler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)
        # TODO: modify format
        fmt = '%(asctime)s | %(name)-14s | %(levelname)-8s | %(message)s'
        fmt_date = '%Y-%m-%d %T %Z'
        formatter = logging.Formatter(fmt, fmt_date)
        self.setFormatter(formatter)


def get_log(name):
    log = logging.getLogger(name)
    log.setLevel('INFO')
    log.addHandler(Handler())
    return log
