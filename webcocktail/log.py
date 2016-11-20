import logging
from pprint import pprint


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


def print_response(r, fields=[]):
    log_format = ('status code: %3s, Content-Length: %5s, url: %s')
    if 'Content-Length' in r.headers:
        length = r.headers['Content-Length']
    else:
        length = len(r.content)
    print(log_format % (r.status_code, length, r.url))

    if not fields:
        fields = ['wct_found_by', 'wct_comments', 'wct_hidden_inputs']
    for field in fields:
        if hasattr(r, field) and r.__dict__[field]:
            print('... %s: %s' % (field, r.__dict__[field]))
