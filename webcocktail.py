#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import config
from webcocktail.webcocktail import WebCocktail


def main():
    parser = argparse.ArgumentParser(
        description='An automatic and lightweight'
        ' web application scanning tool for CTF.')
    parser.add_argument(
        '--cookie', metavar='cookie', default='',
        help='set default cookie for requests')
    parser.add_argument(
        '-debug', action='store_true',
        help='plugins debug mode')
    parser.add_argument(
        '--domain', nargs='*', metavar='d', dest='extra_domain', default=[],
        help='extra carwler doamins')
    parser.add_argument(
        '-no-crawl', dest='crawl', action='store_false', default=True,
        help='without using default crawl')
    parser.add_argument(
        '-no-i', dest='interactive', action='store_false', default=True,
        help='without ipython interactive mode')
    parser.add_argument(
        '-no-scan', dest='scan', action='store_false', default=True,
        help='without using default scan plugin (just using ScanFile plugin)')
    parser.add_argument(
        '--urls', nargs='*', metavar='u', dest='extra_url', default=[],
        help='other pages which you want to crawl')
    parser.add_argument(
        'url', metavar='url',
        help='a website which you want to analysis')
    args = vars(parser.parse_args())
    cookie = args.pop('cookie')
    interactive = args.pop('interactive')

    if cookie:
        config.HEADERS['cookie'] = cookie

    wct = WebCocktail(**args)
    wct.nmap(wct.target)
    results = wct.show_pages()
    if interactive:
        print('\n'
              'IPython Interactive Mode!\n'
              'You can use `wct.show_pages()` to show scanned pages '
              'or using `results` to get responses')
        import IPython
        shell = IPython.terminal.embed.InteractiveShellEmbed()
        shell.mainloop()

if __name__ == '__main__':
    main()
