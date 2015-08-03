import re
from mangaGet2.mangaSite import mangaSite
from mangaGet2.util import bs4, memorize, webpage

class pururin(mangaSite):
    tags = ['p', 'pururin']
    class Series(mangaSite.Series):
        seriesString = '/browse/{}'
        siteTemplate = 'http://www.pururin.com{}'
        soupArgs = {'name': 'div', 'class_': 'stream'}
        
        def __init__(self, series, extras=None, site=None):
            self.series = series
            self.title  = self.runExtras(extras) if extras else series.split('/')[-1].split('.')[0]
            self.title  = ''.join([ch for ch in self.title if ord(ch)<128])
        
        def listPage(self, url):
            soup = bs4(webpage(url).urlObj.read())
            chptrs = [self.Chapter(tag['href'], self) 
                      for tag in soup.find('ul', class_='gallery-list').findAll('a')]
            try:
                nextPage = soup.find('div', class_='pager jumper').find('a', class_='link-next')['href']
                chptrs.extend(self.listPage(self.siteTemplate.format(nextPage)))
                return chptrs
            except:
                return chptrs
        
        def runExtras(self, extras):
            if extras.__class__() == '':
                testThem = [extras]
            elif extras.__class__() == []:
                testThem = extras
            hold = self.series
            for i in testThem:
                if 'search' in i:
                    repls = { ' ': '%20', '-': '%20' }
                    self.seriesTemplate = self.siteTemplate.format('/search?q={}')
                    for i in repls.items():
                        self.series = self.series.replace(*i)
                    return hold.replace(' ', '-')
                if 'single' in i:
                    link = ''.join(['/gallery/', self.series])
                    self.chapters = [self.Chapter(link, self)]
                    return self.series.split('/')[-1].split('.')[0]
        @property
        @memorize
        def chapters(self):
            return self.listPage(self.url)
        
        class Chapter(mangaSite.Series.Chapter):
            pageCut = lambda self: self['href']
            def __init__(self, link, series=None):
                self.link = link
                self.series = series if series else pururin.Series
            
            @property
            def listThem(self):
                thumb = webpage(self.url.replace('gallery', 'thumbs'))
                return thumb.soup.find('ul', class_='thumblist').findAll('a')
            @property
            @memorize
            def title(self):
                soupLoc = self.soup
                name   = ''.join([ch for ch in soupLoc.find('h1').text if ord(ch)<128])
                author = soupLoc.find('td', text=re.compile('Artist*')).parent.a.text
                author = author.replace(' ', '_')
                if '/' in name:
                    name = name.split('/')[0].strip()
                return '[{}]_{}'.format(author, name.replace(' ', '_'))
            
            class Page(mangaSite.Series.Chapter.Page):
                @property
                def imgUrl(self):
                    return pururin.Series.siteTemplate.format(self.soup.find('img', class_='b')['src'])
                @property
                def name(self):
                    return self.imgUrl.split('/')[-1]
