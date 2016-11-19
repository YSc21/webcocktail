#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from webcocktail.webcocktail import WebCocktail


def main():
    parser = argparse.ArgumentParser(
        description='An automatic and lightweight'
        ' web application scanning tool for CTF.')
    parser.add_argument(
        '-domain', nargs='*', metavar='domain', default=[],
        help='extra carwler doamins')
    parser.add_argument(
        '-i', dest='interactive', action='store_true',
        help='with ipython interactive mode')
    parser.add_argument(
        '-noi', dest='interactive', action='store_false', default=True,
        help='without ipython interactive mode (default)')
    parser.add_argument(
        'url', metavar='url',
        help='a website which you want to analysis')
    args = vars(parser.parse_args())
    args['extra_domain'] = args.pop('domain')
    interactive = args.pop('interactive')

    wct = WebCocktail(**args)
    wct.show_pages()
    if interactive:
        print('\n'
              'IPython Interactive Mode!\n'
              'You can use wct.show_pages() to show scanned pages.')
        import IPython
        IPython.embed()

if __name__ == '__main__':
    main()
