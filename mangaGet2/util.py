import functools
import gzip
import io
import os

import random
import re
import socket
import time

import threading 

from HTMLParser import HTMLParser as parser
from bs4 import BeautifulSoup as bs4
#from BeautifulSoup import BeautifulSoup as bs3

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

class Util():
    @staticmethod
    def getUrl(url, buildOpts=[]):
        ret = None
        maxRetries = 3
        headers = [('User-agent', ''.join(['Mozilla/5.0 (X11; U; Linux i686; ',
                    'en-US) AppleWebKit/534.3 (KHTML,like Gecko) ',
                    'Chrome/6.0.472.14 Safari/534.3'])), ('Accept-encoding', 
                    'gzip')]
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
            except urllib2.URLError, Exception:
                if (maxRetries == 0):
                    print('\nUnable to access the internet...')
                    os._exit(1)
                    return
                else:
                    # random dist. for further protection against anti-leech
                    # idea from wget
                    time.sleep(random.uniform(0.5, 1.5))
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

class webpage():
    cookie = []
    
    def __init__(self, url=None):
        if url:
            self.url = url
    @property
    def soup(self):
        return bs4(self.source)
    @property
    @memorize
    def source(self):
        return str(self.urlObj.read())
    @property
    @memorize
    def url(self):
            return self.galTemplate.format(self.gal)
    @property 
    @memorize
    def urlObj(self):
        return Util.getUrl(self.url, self.cookie)
        

class threadIt():
    def __init__(self, meth, inIt, arg):
        self.meth, self.inIt, self.arg = meth, inIt, arg
    
    def run(self):
        threads = []
        for i in self.inIt:
            while threading.activeCount() > 9:
                time.sleep(.15)
            threads.append(threading.Thread(target=self.meth, args=(i, self.arg)))
            threads[-1].daemon = True
            threads[-1].start()
        # Wait for the last thread to finish
        for i in threads:
            if i.isAlive:
                i.join()
                