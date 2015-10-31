import re
from mangaGet2.mangaSite import mangaSite
import mangaGet2.util as util

#Aliases
memorize = util.memorize
webpage  = util.webpage

class mangahere(mangaSite):
    tags = [ 'mh', 'mangahere' ]
    
    class Series(mangaSite.Series):
        seriesString = 'manga/{}/'
        siteTemplate = 'http://www.mangahere.co/{}'
        soupArgs = {'name': 'div', 'class_': 'detail_list'}
        
        @property
        @memorize
        def chapters(self):
            return [self.Chapter(link['href'], self) 
                    for link in self.soup.find(**self.soupArgs).findAll('a')][::-1]
        class Chapter(mangaSite.Series.Chapter):
            @property
            @memorize
            def pages(self):
                return [self.Page(opt['value'], self)
                        for opt in self.soup.find('select', class_='wid60').findAll('option')]
            @property
            @memorize
            def title(self):
                return self.url.split('/')[-2]
                #sel  = lambda tag: tag.has_attr('selected')
                #hold = self.soup.findAll('select')[0].find(sel).text
                #return hold.strip()
            @property
            @memorize
            def url(self):
                return self.link
            class Page(mangaSite.Series.Chapter.Page):
                @property
                @memorize
                def imgUrl(self):
                    return self.soup.find('img', id='image')['src']
                    #url = self.soup.find('img', class_='chapter-img')['src']
                    #return url.strip(' \n').strip().replace(' ', '%20')
                @property
                def name(self):
                    return self.imgUrl.split('/')[-1].split('?')[0]
                @property
                @memorize
                def url(self):
                    return self.page
