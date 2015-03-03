#!/usr/bin/python2.7
import argparse
import cookielib
import mangaGet2.sites

import mangaGet2.util as util
import os
import shutil
import sys

import subprocess
import urllib2
from zipfile import ZipFile

importClass = lambda i: getattr(__import__('mangaGet2.sites.{}'.format(i), fromlist=[i]), i)
sites = [importClass(i) for i in mangaGet2.sites.__all__]

def display(message, level, clrLine=False):
    if clrLine:
        try:
            l = int(subprocess.check_output(['tput', 'cols']))
        except:
            l = 50
        sys.stdout.write('\r{: ^{i}}'.format('', i=l))
    #if level <= results.verb:
    sys.stdout.write(message)
    sys.stdout.flush()
        
def downChap(chapter, dirIt=None):
    baseName = '/'.join([dirIt, chapter.title]) if dirIt else chapter.title
    zipName = '.'.join([baseName, 'cbz'])
    if os.path.exists(zipName):
        return
    mkparentdir(baseName)
    writeStats(chapter, baseName)
    for i in chapter.pages:
        downImage(i, baseName)
    os.remove('/'.join([baseName, '.stats']))
    zipItUp(zipName)
    shutil.rmtree(baseName)
        
def downChapThreading(chapter, dirIt=None):
    baseName = '/'.join([dirIt, chapter.title]) if dirIt else chapter.title
    zipName = '.'.join([baseName, 'cbz'])
    if os.path.exists(zipName):
        return
    mkparentdir(baseName)
    writeStats(chapter, baseName)
    tPages = util.threadIt(downImage, chapter.pages, baseName)
    tPages.run()
    #for i in chapter.pages:
    #    downImage(i, baseName)
    os.remove('/'.join([baseName, '.stats']))
    zipItUp(zipName)
    shutil.rmtree(baseName)
    
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
      
def downSeries(series):
    mkparentdir(series.title)
    total = len(series.chapters)
    display('\nSeries {name} contains {num} chapters.\n'.format(name=series.title, 
                                                              num=total), 1)
    for cur, chap in enumerate(series.chapters, 1):
        display(' '.join(['\r[{:-<10}] Raw:'.format(('+' * (cur*10/total))),
                          '{cur}/{total}    Chapter Name: {name}'.format(cur=cur, total=total, 
                                                                         name=chap.title)]), 1, 1)
        downChapThreading(chap, series.title)
    display('\n', 1)
    
def listAll():
    print('{: <12}{}\n{: <12}{}'.format('Sites', 'Tags', '-----', '----'))
    for num, i in enumerate(sites):
        print('{: <12}{}'.format(''.join([mangaGet2.sites.__all__[num], ':']), ', '.join(i.tags)))
    sys.exit()

def loadCookie(fileName):
    cookies = cookielib.MozillaCookieJar(filename=fileName)
    cookies.load()
    #handler = urllib2.HTTPHandler(debuglevel=1)
    return [urllib2.HTTPCookieProcessor(cookies)]

def mkparentdir(dirName):
    dirHold = os.path.realpath('.')
    testStrList = dirName.split('/')
    for i in testStrList:
        dirHold = '/'.join([dirHold, i])
        if not os.path.exists(dirHold):
            os.mkdir(dirHold)
            
def writeStats(chapter, dirIt):
    with open('/'.join([dirIt, '.stats']), 'w') as f:
        f.write('Link: {}\n'.format(chapter.url))
        f.write('Total: {}'.format(chapter.pages_len))

def zipItUp(zipName, zipItArgs='w'):
    zipIt = ZipFile(zipName, zipItArgs)
    for root, dirs, files in os.walk(zipName.split('.cbz')[0]):
        for f in files:
            zipIt.write('/'.join([root, f]),'/'.join([root.split('/')[-1], f]))
    zipIt.close()
    
def searchIt(site, searchString):
    fullTable, nameLen = site.runSearch(searchString), 0
    bold, end = '\033[1m', '\033[0m'
    for i in fullTable:
        if nameLen < len(i['name']):
            nameLen = len(i['name'])+3
    display(bold, 0)
    display('\t'.join(['\n{: <{}}'.format('Name', nameLen), 'Latest Chapter', 'Date of update']), 0)
    display(''.join([end, '\n']), 0)              
    for n, i in enumerate(fullTable, 1):
        numPrint = ''.join(['{: <14}'.format(i['lChap']), '\t', i['dou'], '\n'])
        display('\t'.join(['{}. {: <{}}'.format(n, i['name'], nameLen-3), numPrint]), 0)
    selection = raw_input('Please select one of the above: ')
    return site.Series(fullTable[int(selection)-1]['serString'])
    
def main(site, series, chap=None, extras=None, search=None):
    if search:
      hold = searchIt(site, series)
    else:
      hold = site.Series(series, extras)
    if chap:
        downChapThreading(hold.chapters[chap-1])
    else:
        downSeries(hold)

    
if __name__ == '__main__':
    #sitesSupported = str()
    #for i in sites:
    #    sitesSupported += '\t{}: {} or {}'.format(i.__module__.split('.')[-1], 
    #                                              ', '.join(i.tags[:-1]), i.tags[-1])
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
    
    results = parser.parse_args()
    cookie=None
    args = {}
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
    args.update({'search': results.search})
    args.update({'series': results.series})
    if results.chapter:
        args.update({'chap': results.chapter})
    if results.extras:
        args.update({'extras': results.extras})
    main(**args)