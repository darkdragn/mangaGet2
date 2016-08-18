#!/usr/bin/env python2
import argparse
import os
import requests
import shutil
import signal
import sys

from mangaGet2 import sites
from mangaGet2.util import display, mkparentdir, threadIt, writeStats, zipItUp

site_list = [getattr(sites, name) for name in sites.__all__]


def listAll():
    print('{: <12}{}\n{: <12}{}'.format('Sites', 'Tags', '-----', '----'))
    for num, i in enumerate(site_list):
        print('{: <12}{}'.format(''.join([sites.__all__[num], ':']),
              ', '.join(i.tags)))
    sys.exit()


def sigIntHandler(signal, frame):
    print("\nSigInt caught. Exiting...")
    sys.exit()


class main():
    def __init__(self, site, series, chap=None, chapLast=None,
                 extras=None, search=None, top=None, thread=None):
        self.site, self.seriesStr = site, series
        self.chapl, self.top = chapLast, top
        self.extras, self.thread = extras, thread
        self.series = self.searchIt() if search \
            else site.Series(series, extras, site)
        self.downChapThread(self.series.chapters[chap-1]) if chap \
            else self.downSeries()

    @staticmethod
    def downImage(page, dir=None):
        while True:
            try:
                writeName = page.name
                if dir:
                    writeName = '/'.join([dir, writeName])
                if os.path.exists(writeName):
                    return
                img = requests.get(page.image.url)
                with open(writeName, 'wb') as f:
                    f.write(img.content)
                break
            except AttributeError:
                raise
                break

    def downChapThread(self, chapter, dirIt=None):
        baseName = '/'.join([dirIt, chapter.title]) if dirIt else chapter.title
        zipName = '.'.join([baseName, 'cbz'])
        if os.path.exists(zipName):
            return
        mkparentdir(baseName)
        writeStats(chapter, baseName)
        if self.thread == 1:
            start = next(len(i[2])-1 for i in os.walk(baseName))
            start = start if start >= 0 else 0
            for i in chapter.pages[start:]:
                try:
                    self.downImage(i, baseName)
                except TypeError:
                    with open('test', 'wb') as f:
                        f.write(i.source)
        else:
            threadIt(self.downImage, chapter.pages, baseName).run(self.thread)
        zipItUp(zipName)
        shutil.rmtree(baseName)

    def downSeries(self):
        title = self.series.title
        if self.top:
            mkparentdir(title)
        total = self.chapl if self.chapl else len(self.series.chapters)
        display('\nSeries {name} contains {num} chapters.\n'.format(name=title,
                                                                    num=total))
        chapList = self.series.chapters[-self.chapl:] if self.chapl \
            else self.series.chapters
        for cur, chap in enumerate(chapList, 1):
            ticker = '\r[{:-<10}] Raw:'.format(('+' * ((cur)*10/total)))
            status = '{}/{}    Chapter Name: {}'.format(cur, total, chap.title)
            display(' '.join([ticker, status]), 1, 1)
            self.downChapThread(chap, title if self.top else None)
        display('\n')

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
    parser.add_argument('-n', action='store_false', dest='top',
                        help='Disable top level folder.')
    parser.add_argument('-s', action='store', dest='site', default='mp',
                        metavar='site', help='Specify a site.')
    parser.add_argument('-se', action='store_true', dest='search',
                        default=False, help='Search a site.')
    parser.add_argument('-sl', action='store_true', dest='list',
                        help='List all supported sites.')
    parser.add_argument('-t', action='store', dest='thread', default=10,
                        metavar='thread', type=int,
                        help='Specify the number of threads allowed to run.')
    parser.add_argument('-x', action='store', dest='extras', default=None,
                        metavar='extras', help='Specify extra options.')
    parser.add_argument('-v', action='store', dest='verb', type=int, default=1,
                        help='Specify a verbosity.', metavar='verbosity')
    parser.set_defaults(top=True)
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
