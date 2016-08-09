import functools
import ghost 
import gzip
import io

import os
import random
import re
import socket

import subprocess
import sys
import time

from bs4 import BeautifulSoup as bs4
from HTMLParser import HTMLParser as parser
from Queue import Queue

from threading import Thread
from zipfile import ZipFile

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

Ghost = ghost.Ghost
###############################################################################
#########################  Begin some standard defs. ##########################
###############################################################################
def display(message, level=0, clrLine=False):
    if clrLine:
        try:
            l = int(subprocess.check_output(['tput', 'cols']))
        except:
            l = 50
        sys.stdout.write('\r{: ^{i}}'.format('', i=l))
    #if level <= results.verb:
    sys.stdout.write(message)
    sys.stdout.flush()

def initBrowser(url):
    br = Ghost()
    session = br.start() #download_images=False)
    session.wait_timeout = 15
    
    session.open(url)
    time.sleep(5)
    while True:
        try:
            session.open(url)
            break
        except ghost.ghost.TimeoutError as e:
            pass
    return session
    
def loadCookie(fileName):
    cookies = cookielib.MozillaCookieJar(filename=fileName)
    cookies.load()
    #handler = urllib2.HTTPHandler(debuglevel=1)
    return [urllib2.HTTPCookieProcessor(cookies)]
# :SEE: http://wiki.python.org/moin/PythonDecoratorLibrary/#Alternate_memoize_as_nested_functions
def memorize(obj):
    cache = obj.cache = {}
    
    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer

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
        f.write('Total: {}'.format(len(chapter.pages)))

def zipItUp(zipName, zipItArgs='w'):
    zipIt = ZipFile(zipName, zipItArgs)
    for root, dirs, files in os.walk(zipName.split('.cbz')[0]):
        for f in files:
            zipIt.write('/'.join([root, f]),'/'.join([root.split('/')[-1], f]))
    zipIt.close()

###############################################################################
########################  Begin class declarations.  ##########################
###############################################################################
class threadIt():
    def __init__(self, meth, objs, arg):
        self.meth, self.objs, self.arg = meth, objs, arg
        self.queue = Queue()
    
    def downPage(self):
        while not self.queue.empty():
            page = self.queue.get()
            self.meth(page, self.arg)
            self.queue.task_done()
    def run(self, num=10):
        for i in self.objs:
            self.queue.put(i)
        for i in range(num):
            worker = Thread(target = self.downPage)
            worker.setDaemon(True)
            worker.start()
        self.queue.join()

class Util():
    @staticmethod
    def getUrl(url, buildOpts=[]):
        ret = None
        maxRetries = 3
        headers = [('User-agent', ''.join(['Mozilla/5.0 (X11; U; Linux i686; ',
                    'en-US) AppleWebKit/534.3 (KHTML,like Gecko) ',
                    'Chrome/6.0.472.14 Safari/534.3']))]#, ('Accept-encoding', 
                    #'gzip')]
        opener = urllib2.build_opener(*buildOpts)
        opener.addheaders = headers
        while (ret == None):
            try:
                readIt = opener.open(url, timeout=20)
                encoding = readIt.headers.get('Content-Encoding')
                if encoding == None:
                    ret = readIt
                else:
                    if encoding.upper() == 'GZIP':
                        compressedstream = io.BytesIO(readIt.read())
                        gzipper = gzip.GzipFile(fileobj=compressedstream)
                        ret = gzipper
                    else:
                        raise RuntimeError('Unknown HTTP Encoding returned')
            except (urllib2.URLError, socket.timeout) as e:
                if (maxRetries == 0):
                    print('\nUnable to access the internet...')
                    print url
                    return
                else:
                    # random dist. for further protection against anti-leech
                    # idea from wget
                    time.sleep(random.uniform(1.0, 2.5))
                    maxRetries -= 1
        return ret
    
    @staticmethod
    def unescape(inputStr):
        return parser().unescape(inputStr)
      
    @staticmethod
    def normalizeName(inputStr):
        repls = [('/', '-'), (' ', '_'), ('.', '_'), ('&quot;', '')]
        for repl in repls:
	    inputStr = inputStr.replace(*repl)
	output = "".join([ch for ch in inputStr if ord(ch)<128])
	return Util.unescape(re.sub('__*', '_', output))

class webpage():
    cookie = []
    
    def __init__(self, url=None, br=None):
        if url:
            self.url = url
        if br:
            self.br = br
    @property
    def soup(self):
        return bs4(self.source, 'lxml')
    @property
    @memorize
    def source(self):
        if hasattr(self, 'br'):
            #counter = 4
            while True: #counter:
                try:
                    #print self.url
                    page, res = self.br.open(self.url)
                    self.page = page
                    if page.http_status is 200:
                        break
                    time.sleep(1)
                except ghost.ghost.TimeoutError as e:
                    #counter -= 1
                    time.sleep(.5)
            return str(page.content)
        return str(self.urlObj.read())
    @property
    def urlObj(self):
        return Util.getUrl(self.url, self.cookie)
