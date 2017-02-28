from difflib import unified_diff
import logging
from pprint import pprint
import re

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


def _print_diff_result(diff, max_diff_line):
    lines = list(diff)[2:]
    if len(lines) > max_diff_line:
        lines = lines[:max_diff_line]  # limit printed lines
        lines.append('...\n')

    for i in range(len(lines)):
        if lines[i][0] == '+':
            lines[i] = get_color(lines[i], CYAN)
            for e in ['notice', 'warning', 'error']:
                pattern = re.findall(e, lines[i], re.IGNORECASE)
                for p in pattern:
                    replace = (get_color(p, YELLOW) +
                               (COLOR_SEQ % (FOREGROUND + CYAN)))
                    lines[i] = lines[i].replace(p, replace)
    print(''.join(lines))
    print('')


def get_color(msg, color):
    return (COLOR_SEQ % (FOREGROUND + color) + msg + RESET_SEQ)


def get_log(name):
    log = logging.getLogger(name)
    log.setLevel('INFO')
    log.addHandler(Handler())
    return log


def print_response(number, r, pages, fields=[], max_diff_line=30):
    # basic info
    log_format = ('status code: %3s, Content-Length: %5s, url: %s')
    log_format = get_color('%02d. ' % number, GREEN) + log_format
    length = '-'
    if 'Content-Length' in r.headers:
        length = r.headers['Content-Length']
    url = r.url
    if r.wct_found_by == 'ScanFile':
        url = get_color(r.url, YELLOW)
    print(log_format % (r.status_code, length, url))

    # 302 redirect
    if r.history:
        print('    history: %s' % get_color(str(r.history), YELLOW))
    if r.status_code == 302:
        print('    redirect to: %s' % get_color(r.headers['Location'], YELLOW))

    # fields
    if not fields:
        fields = [field for field in r.__dict__ if field.startswith('wct_')]
    for field in fields:
        if hasattr(r, field) and r.__dict__[field]:
            msg = str(r.__dict__[field])
            if field == 'wct_comments' or field == 'wct_hidden_inputs':
                msg = get_color(msg, YELLOW)
            print('    %s: %s' % (field, msg))

    # robots.txt
    if 'robots.txt' in r.url:
        print('%s' % get_color(r.text, YELLOW))
    # diff
    url_path, _ = utils.get_path_hash(r)
    first_r = [p for p in pages if utils.get_path_hash(p)[0] == url_path][0]
    diff = unified_diff(first_r.text.splitlines(keepends=True),
                        r.text.splitlines(keepends=True),
                        fromfile=first_r.url, tofile=r.url)
    _print_diff_result(diff, max_diff_line)

import webcocktail.utils as utils
