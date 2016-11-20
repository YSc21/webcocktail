import logging
from pprint import pprint

FOREGROUND = 30
BACKGROUND = 40
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    'DEBUG': BLUE,
    'INFO': WHITE,
    'WARNING': YELLOW,
    'ERROR': RED,
    'CRITICAL': MAGENTA,
}

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


class Formatter(logging.Formatter):
    def __init__(self, fmt, datefmt):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, record):
        levelname = record.levelname
        msg = record.msg
        if levelname in COLORS:
            record.levelname = get_color(levelname, COLORS[levelname])
        if 'Found' in msg:
            record.msg = get_color(msg, GREEN)
        return logging.Formatter.format(self, record)


class Handler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)
        fmt = '%(asctime)s | %(name)-14s | %(levelname)-8s | %(message)s'
        datefmt = '%Y-%m-%d %T %Z'
        formatter = Formatter(fmt, datefmt)
        self.setFormatter(formatter)


def get_color(msg, color):
    return (COLOR_SEQ % (FOREGROUND + color) + msg + RESET_SEQ)


def get_log(name):
    log = logging.getLogger(name)
    log.setLevel('INFO')
    log.addHandler(Handler())
    return log


def print_response(r, fields=[]):
    log_format = ('status code: %3s, Content-Length: %5s, url: %s')
    if 'Content-Length' in r.headers:
        length = r.headers['Content-Length']
    else:
        length = len(r.content)
    print(log_format % (r.status_code, length, r.url))

    if not fields:
        for field in r.__dict__:
            if field.startswith('wct_'):
                print('... %s: %s' % (field, r.__dict__[field]))
    for field in fields:
        if hasattr(r, field) and r.__dict__[field]:
            print('... %s: %s' % (field, r.__dict__[field]))
