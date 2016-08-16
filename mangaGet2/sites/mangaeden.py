import re
# from mangaGet2 import mangaSite
from .. import mangaSite
from ..util import memorize, webpage

tags = [ 'me', 'mangaeden' ]
siteTemplate = 'http://www.mangaeden.com{}'
searchTemplate = siteTemplate.format('/en-directory/?title={}')
      
class Series(mangaSite.Series):
    seriesString = '/en-manga/{}/'
    siteTemplate = 'http://www.mangaeden.com{}'
    soupArgs = {'name': 'a', 'class_': 'chapterLink'}
    
    class Chapter(mangaSite.Chapter):
        listArgs = {'name': 'select', 'id': 'pageSelect'}
        @property
        def title(self):
            orig = self.url.split('/')[-3]
            padIt = lambda x: '{:0>3}'.format(int(x))
            if '.' in orig:
                hold = orig.split('.')
                return '.'.join([padIt(hold[0]), hold[1]])
            return padIt(orig)

    class Page(mangaSite.Page):
        @property
        @memorize
        def imgUrl(self):
            raw = self.soup.find('img', id='mainImg')
            return 'http:{}'.format(raw['src'])
        @property
        def name(self):
            return '.'.join(['{:0>3}'.format(self.page.split('/')[-2]), 
                             self.imgUrl.split('.')[-1]])
