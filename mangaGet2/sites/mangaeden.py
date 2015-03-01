import re
from mangaGet2.mangaSite import mangaSite
from mangaGet2.util import memorize

class mangaeden(mangaSite):
    tags = [ 'me', 'mangaeden' ]
    class Series(mangaSite.Series):
        siteTemplate = 'http://www.mangaeden.com{}'
        seriesTemplate = siteTemplate.format('/en-manga/{}/')
        soupArgs = {'name': 'a', 'class_': 'chapterLink'}
        
        class Chapter(mangaSite.Series.Chapter):
            @property
            @memorize
            def listThem(self):
                return self.soup.find('div', class_="pagination ").findAll('a', text=re.compile('[0-9]'))[1:]
            @property
            def title(self):
                orig = self.url.split('/')[-3]
                padIt = lambda x: '{:0>4}'.format(x)
                if '.' in orig:
                    hold = orig.split('.')
                    return '.'.join([padIt(hold[0]), hold[1]])
                return padIt(orig)
            class Page(mangaSite.Series.Chapter.Page):
                @property
                @memorize
                def imgUrl(self):
                    return ''.join(['http:', self.soup.find('img', id='mainImg')['src']])
                @property
                def name(self):
                    return '.'.join(['{:0>3}'.format(self.page.split('/')[-2]), 
                                     self.imgUrl.split('.')[-1]])