#!/usr/bin/env python2
import argparse
import mangaGet2.sites
import shutil
import signal

from mangaGet2.util import *

importClass = lambda i: getattr(__import__('mangaGet2.sites.{}'.format(i), 
                                           fromlist=[i]), i)
sites = [importClass(i) for i in mangaGet2.sites.__all__]

def listAll():
    print('{: <12}{}\n{: <12}{}'.format('Sites', 'Tags', '-----', '----'))
    for num, i in enumerate(sites):
        print('{: <12}{}'.format(''.join([mangaGet2.sites.__all__[num], ':']), ', '.join(i.tags)))
    sys.exit()

def sigIntHandler(signal, frame):
    print("\nSigInt caught. Exiting...")
    sys.exit()
    
class main():
    def __init__(self, site, series, chap=None, extras=None, search=None):
        self.site, self.seriesStr = site, series
        self.extras = extras
        self.series = self.searchIt() if search else site.Series(series, extras, site)
        downChapThreading(self.series.chapters[chap-1]) if chap else self.downSeries()
    
    @staticmethod
    def downImage(page, dir=None):
        writeName = page.name
        if dir: 
            writeName = '/'.join([dir, writeName])
        if os.path.exists(writeName):
            return
        while True:
            try:
                img = page.image
                if img.data:
                    with open(writeName, 'wb') as f:
                        f.write(img.data)
                break
            except:
                if 'img' in locals():
                    del img
                if os.path.exists(writeName):
                    os.remove(writeName)
    def downChapThreading(self, chapter, dirIt=None):
        baseName = '/'.join([dirIt, chapter.title]) if dirIt else chapter.title
        zipName = '.'.join([baseName, 'cbz'])
        if os.path.exists(zipName):
            return
        mkparentdir(baseName)
        writeStats(chapter, baseName)
        threadIt(self.downImage, chapter.pages, baseName).run()
        os.remove('/'.join([baseName, '.stats']))
        zipItUp(zipName)
        shutil.rmtree(baseName)
    def downSeries(self):
        title = self.series.title
        mkparentdir(title)
        total = len(self.series.chapters)
        display('\nSeries {name} contains {num} chapters.\n'.format(name=title, 
                                                                    num=total))
        for cur, chap in enumerate(self.series.chapters, 1):
            ticker = '\r[{:-<10}] Raw:'.format(('+' * ((cur-1)*10/total)))
            status = '{}/{}    Chapter Name: {}'.format(cur, total, chap.title)
            display(' '.join([ticker, status]), 1, 1)
            self.downChapThreading(chap, title)
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
        return self.site.Series(fullTable[int(selection)-1]['serString'], site=self.site)
        
if __name__ == '__main__':
    parser=argparse.ArgumentParser('MangaGet2 Cli')
    parser.add_argument('series', action='store', metavar='series', nargs='?', 
                        help='Unique identifier for the series to rip.')
    parser.add_argument('-c', action='store', dest='chapter', default=None, 
                        metavar='chapter', type=int, help='Specify a single chapter.')
    parser.add_argument('-s', action='store', dest='site', default='mp', 
                        metavar='site', help='Specify a site.')
    parser.add_argument('-se', action='store_true', dest='search', default=False,
                        help='Search a site.')
    parser.add_argument('-sl', action='store_true', dest='list', 
                        help='List all supported sites.')
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
    for i in sites:
        for tag in i.tags:
            if results.site == tag:
                args.update({'site': i})
                break
    args.update({'search': results.search, 'series': results.series,
                 'chap': results.chapter,  'extras': results.extras})
    main(**args)
