#!/usr/bin/env python2
import argparse
import mangaGet2.sites
import requests
import shutil
import signal
import socket

from mangaGet2.util import *

importClass = lambda i: getattr(__import__('mangaGet2.sites.{}'.format(i), 
                                           fromlist=[i]), i)
sites = [importClass(i) for i in mangaGet2.sites.__all__]

def listAll():
    print('{: <12}{}\n{: <12}{}'.format('Sites', 'Tags', '-----', '----'))
    for num, i in enumerate(sites):
        print('{: <12}{}'.format(''.join([mangaGet2.sites.__all__[num], ':']), 
              ', '.join(i.tags)))
    sys.exit()

def sigIntHandler(signal, frame):
    print("\nSigInt caught. Exiting...")
    sys.exit()
    
class main():
    def __init__(self, site, series, chap=None, chapLast = None, 
                 extras=None, search=None, top=None, thread=None):
        self.site, self.seriesStr = site, series
        self.chapl, self.top = chapLast, top
        self.extras, self.thread = extras, thread
        self.series = self.searchIt() if search else site.Series(series, extras, site)
        self.downChapThread(self.series.chapters[chap-1]) if chap else self.downSeries()
    
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
            except AttributeError as ae:
                raise
                break
            #except socket.timeout as st:
                #pass
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
                except TypeError as te:
                    with open('test', 'wb') as f:
                        f.write(i.source)
        else:
            threadIt(self.downImage, chapter.pages, baseName).run(self.thread)
        #os.remove('/'.join([baseName, '.stats']))
        zipItUp(zipName)
        shutil.rmtree(baseName)
    def downSeries(self):
        title = self.series.title
        if self.top:
            mkparentdir(title)
        total = self.chapl if self.chapl else len(self.series.chapters)
        display('\nSeries {name} contains {num} chapters.\n'.format(name=title, 
                                                                    num=total))
        chapList = self.series.chapters[-self.chapl:] if self.chapl else self.series.chapters
        for cur, chap in enumerate(chapList, 1):
            ticker = '\r[{:-<10}] Raw:'.format(('+' * ((cur)*10/total)))
            status = '{}/{}    Chapter Name: {}'.format(cur, total, chap.title)
            display(' '.join([ticker, status]), 1, 1)
            self.downChapThread(chap, title if self.top else None)
        display('\n')
    def searchIt(self):
        fullTable, nameLen = self.site.runSearch(self.seriesStr), 0
        bold, end = '\033[1m', '\033[0m'
        for i in fullTable:
            nameLen = len(i['name']) if len(i['name'])>nameLen else nameLen
        display('\t'.join(['\n{}{: <{}}'.format(bold, 'Name', nameLen+3), 
                          'Latest Chapter', 'Date of update{}\n'.format(end)]))             
        for n, i in enumerate(fullTable, 1):
            numPrint = ''.join(['{: <14}'.format(i['lChap']), '\t', i['dou'], '\n'])
            try:
                disPrint = '\t'.join(['{}. {: <{}}'.format(n, i['name'], 
                                                           nameLen), numPrint])
            except:
                ln  = nameLen + (len(i['name'].encode('utf-16')[2:])/2)
                name = '{}. {: <{}}'.format(n, i['name'].encode('utf-16')[2:], ln)
                num = numPrint.encode('utf-16')[2:]
                disPrint = '\t'.join([name, num])
            display(disPrint)
        selection = raw_input('Please select one of the above: ')
        return self.site.Series(fullTable[int(selection)-1]['serString'], 
                                site=self.site)
        
if __name__ == '__main__':
    parser=argparse.ArgumentParser('MangaGet2 Cli')
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
                        help='Specify the number of threads allowed to run.' )
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
    for i in sites:
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
