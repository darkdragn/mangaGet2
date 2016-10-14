#!/usr/bin/env python2
import argparse
import signal
import sys

from mangaGet2 import main, site_list
from mangaGet2 import sites


def listAll():
    len = 15
    print('{: <{len}}{}\n{: <{len}}{}'.format('Sites', 'Tags', '-----',
          '----', len=len))
    for num, i in enumerate(site_list):
        print('{: <{len}}{}'.format(''.join([sites.__all__[num][:len-2], ':']),
              ', '.join(i.tags), len=len))
    sys.exit()


def sigIntHandler(signal, frame):
    global thread
    print("\nSigInt caught. Exiting...")
    if 'thread' in globals():
        thread.kill()
    sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser('MangaGet2 Cli')
    parser.add_argument('series', action='store', metavar='series', nargs='?',
                        help='Unique identifier for the series to rip.')
    parser.add_argument('-c', action='store', dest='chapter', default=None,
                        metavar='chapter', type=int,
                        help='Specify a single chapter.')
    parser.add_argument('-l', action='store', dest='chapLast', default=None,
                        metavar='chapLast', type=int,
                        help='Specify a number of chapters, latest back.')
    parser.add_argument('-n', action='store_false', dest='top', default=True,
                        help='Disable top level folder.')
    parser.add_argument('-s', action='store', dest='site', default='mp',
                        metavar='site', help='Specify a site.')
    parser.add_argument('-se', action='store_true', dest='search',
                        default=False, help='Search a site.')
    parser.add_argument('-sl', action='store_true', dest='list',
                        help='List all supported sites.')
    parser.add_argument('-t', action='store', dest='thread', default=4,
                        metavar='thread', type=int,
                        help='Specify the number of threads allowed to run.')
    parser.add_argument('-x', action='store', dest='extras', default=None,
                        metavar='extras', help='Specify extra options.')
    parser.add_argument('-v', action='store', dest='verb', type=int, default=1,
                        help='Specify a verbosity.', metavar='verbosity')
    results, args = parser.parse_args(), {}
    signal.signal(signal.SIGINT, sigIntHandler)
    if results.list:
        listAll()
    if not results.list and not results.series:
        parser.print_help()
        sys.exit()
    for i in site_list:
        for tag in i.tags:
            if results.site == tag:
                args.update({'site': i})
                break
    args.update({'search': results.search, 'series': results.series,
                 'chap': results.chapter,  'extras': results.extras,
                 'chapLast': results.chapLast, 'top': results.top,
                 'thread': results.thread})
    if hasattr(args['site'], 'defaults'):
        args.update(args['site'].defaults)
    main(**args)
