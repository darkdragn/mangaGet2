import ghost
import re
import time
import mangaGet2.util as util

from bs4 import BeautifulSoup as bs4
from mangaGet2.mangaSite import mangaSite

#Aliases
memorize = util.memorize
webpage  = util.webpage

class fakku(mangaSite):
    tags = [ 'f', 'fakku' ]
    
    class Series(mangaSite.Series):
        seriesString = '/doujinshi/{}/read'
        siteTemplate = 'http://www.fakku.net{}'

        @property
        @memorize
        def br(self):
            return self.initGhost()
        @property
        @memorize
        def chapters(self):
            return [ self.Chapter(self.seriesTemplate.format(self.series), self) ]
        def initGhost(self):
            Ghost = ghost.Ghost()
            br = Ghost.start()
            return br
        
        class Chapter(mangaSite.Series.Chapter):
            def __init__(self, link, series):
                self.url = link
                self.series = series
                self.br = series.br
            
            @property
            @memorize
            def pages(self):
                hold = self.soup.find('div', id='thumbs').findAll('a')
                return [self.Page(''.join([self.url, i['href']]), self) for i in hold]
            @property
            @memorize
            def soup(self):
                try:
                    self.br.open(self.url)
                except ghost.TimeoutError:
                    pass
                return bs4(self.br.content)
            @property
            def title(self):
                return url.split('/')[4]
            class Page(mangaSite.Series.Chapter.Page):
                br = ghost.Ghost().start()
                def __init__(self, page, chapter):
                    self.chapter = chapter
                    self.cookie  = chapter.cookie
                    self.url     = page

                @property
                @memorize
                def imgUrl(self):
                    return self.soup.find('img', class_='current-page')['src']
                @property
                def name(self):
                    return '.'.join(['{:0>3}'.format(self.page.split('/')[-2]),
                                     self.imgUrl.split('.')[-1]])
                def brLoad(self, url):
                    try:
                        self.br.open(url)
                    except ghost.TimeoutError as e:
                        pass
                @property
                @memorize
                def soup(self):
                    self.br.wait_timeout = 2
                    print self.url
                    self.brLoad(self.url)
                    self.brLoad(self.url)
                    return bs4(self.br.content)
