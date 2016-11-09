#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from webcocktail.webcocktail import WebCocktail


def main():
    parser = argparse.ArgumentParser(
        description='Webcocktail: '
        'an automatic and lightweight web application fuzzing tool for CTF')
    parser.add_argument(
        '-domain', nargs='*', metavar='domain',
        help='extra carwler doamins')
    parser.add_argument(
        'url', metavar='url',
        help='a website which you want to analysis')
    args = vars(parser.parse_args())
    args['extra_domain'] = args.pop('domain')

    wct = WebCocktail(**args)
    wct.show_pages()

if __name__ == '__main__':
    main()
