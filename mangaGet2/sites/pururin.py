import ghost
import re

from mangaGet2.mangaSite import mangaSite
from mangaGet2.util import bs4, initBrowser, loadCookie, memorize, time, webpage

class pururin(mangaSite):
    tags = ['p', 'pururin']
    class Series(mangaSite.Series):
        seriesString = '/browse/{}'
        siteTemplate = 'http://www.pururin.com{}'
        soupArgs = {'name': 'div', 'class_': 'stream'}
        
        def __init__(self, series, extras=None, site=None):
            self.br = initBrowser(self.siteTemplate.format(''))
            self.series = series
            self.title  = self.runExtras(extras) if extras else series.split('/')[-1].split('.')[0]
            self.title  = ''.join([ch for ch in self.title if ord(ch)<128])
        
        def listPage(self, url):
            soup = bs4(webpage(url, self.br).source)
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
                elif 'single' in i:
                    link = ''.join(['/gallery/', self.series])
                    self.chapters = [self.Chapter(link, self)]
                    return self.series.split('/')[-1].split('.')[0]
                elif 'cook' in i:
                    self.cookie = loadCookie(i.split('=')[-1])
        @property
        @memorize
        def chapters(self):
            return self.listPage(self.url)
            #for i in pages:
                #print i.url
            #return pages
        
        class Chapter(mangaSite.Series.Chapter):
            pageCut = lambda self, i: i['href']
            def __init__(self, link, series=None):
                self.link = link
                self.series = series if series else pururin.Series
                self.br = series.br
            
            #@property
            def listThem(self):
                thumb = webpage(self.url.replace('gallery', 'thumbs'), self.br)
                return thumb.soup.find('ul', class_='thumblist').findAll('a')
            @property
            @memorize
            def title(self):
                soup = self.soup
                try:
                    name = ''.join([ch for ch in soup.find('h1').text 
                                    if ord(ch)<128])
                    artSnip = soup.find('td', text=re.compile('Artist*'))
                    author = artSnip.parent.a.text
                except AttributeError as e:
                    print self.page.http_status
                    print self.source
                    print self.url
                    raise
                author = author.replace(' ', '_')
                if '/' in name:
                    name = name.split('/')[0].strip()
                return '[{}]_{}'.format(author, name.replace(' ', '_'))
            
            class Page(mangaSite.Series.Chapter.Page):
                @property
                def br(self):
                    return self.chapter.br
                @property
                def image(self):
                    return self.chapter.Image(self.imgUrl, self)
                @property
                def imgUrl(self):
                    snip = self.soup.find('img', class_='b')['src']
                    return pururin.Series.siteTemplate.format(snip)
                @property
                def name(self):
                    return self.imgUrl.split('/')[-1]
            class Image():
                def __init__(self, url, page):
                    self.nameIt=page.name
                    self.page = page
                    self.url = url
                @property
                def data(self):
                    counter = 4
                    while counter:
                        try:
                            image, res = self.page.br.open(self.url)
                            if image.http_status is 200:
                                break
                            time.sleep(1)
                        except ghost.ghost.TimeoutError as e:
                            counter -= 1
                            time.sleep(.5)
                    return image.content
