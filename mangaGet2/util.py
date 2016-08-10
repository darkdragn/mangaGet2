import functools
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
            try:
                self.meth(page, self.arg)
            except socket.timeout as e:
                self.queue.put(page)
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
    
    def __init__(self, url=None):
        if url:
            self.url = url
    @property
    def soup(self):
        return bs4(self.urlObj.content, 'html.parser')
    @property
    @memorize
    def source(self):
        return str(self.urlObj.content)
    @property
    def urlObj(self):
        return requests.get(self.url)
