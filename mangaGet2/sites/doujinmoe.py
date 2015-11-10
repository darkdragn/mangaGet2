import ghost
import re
import time
import mangaGet2.util as util

from bs4 import BeautifulSoup as bs4
from mangaGet2.mangaSite import mangaSite

#Aliases
memorize = util.memorize
webpage  = util.webpage

class doujinmoe(mangaSite):
    tags = [ 'dm', 'doujin-moe' ]
    
    class Series(mangaSite.Series):
        seriesString = '/{}'
        siteTemplate = 'http://www.doujin-moe.us{}'

        def __init__(self, series, extras=None, site=None):
            self.extras = extras
            self.series = series
            if self.extras:
                self.runExtras()

        @property
        @memorize
        def chapters(self):
            chapt = []
            for i in self.soup.find('span', class_='pagelist').findAll('a'):
                hold = webpage(''.join([self.url, '?page=', i.text]))
                chapt.extend(
                        self.Chapter(self.siteTemplate.format(i['href']),self)
                    for i in hold.soup.find('div',
                        id='foldercontent').findAll('a'))
            return chapt            
        def runExtras(self):
            if 'single' in self.extras:
                chapUrl = self.seriesTemplate.format(self.series)
                self.chapters = [self.Chapter(chapUrl, self)]
        @property
        def title(self):
            return '->'.join([i.text.replace(' ', '_') for i in
                self.soup.find('div', class_='title').findAll('a')])
        
        class Chapter(mangaSite.Series.Chapter):
            def __init__(self, chap, series):
                self.url = chap
            
            @property
            @memorize
            def pages(self):
                return [self.Page(i['file'], self, num) for num, i in
                        enumerate(self.soup.findAll('djm'))]
            @property
            def title(self):
                return '->'.join([i.text.replace(' ', '_') for i in
                    self.soup.find('div', class_='title').findAll('a')])
            class Page(mangaSite.Series.Chapter.Page):
                def __init__(self, page, chapter, number):
                    self.url = page
                    self.chapter = chapter
                    self.num = number
                @property
                @memorize
                def imgUrl(self):
                    return self.url
                @property
                @memorize
                def name(self):
                    ext = self.url.split('?')[0].split('.')[-1]
                    return '{:03d}.{}'.format(self.num, ext)
