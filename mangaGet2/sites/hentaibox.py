import re
from mangaGet2.mangaSite import mangaSite
import mangaGet2.util as util

#Aliases
memorize = util.memorize
webpage  = util.webpage

class hentaibox(mangaSite):
    tags = [ 'hb', 'hentaibox' ]
    defaults = {'top': False}
    
    class Series(mangaSite.Series):
        seriesString = '/hentai-manga/{}&load=all'
        siteTemplate = 'http://www.hentaibox.net{}'
        soupArgs = {'name': 'table', 'class_': 'table table-hover'}
        
        @property
        def chapters(self):
            return [self.Chapter(self.url, self)]
        #@property
        #@memorize
        #def chapters(self):
        #    return [self.Chapter(link['href'], self) 
        #            for link in self.soup.find(**self.soupArgs).findAll('a')]
        class Chapter(mangaSite.Series.Chapter):
            @property
            def url(self):
                return self.link
            @property
            @memorize
            def pages(self):
                return [self.Page(opt['href'], self)
                        for opt in self.soup.find('table',
                            class_="search_gallery").findAll('a')]
            @property
            @memorize
            def title(self):
                return self.soup.h2.text.split('/')[-1].strip().replace(' ',
                        '_')
            class Page(mangaSite.Series.Chapter.Page):
                @property
                def url(self):
                    return self.page
                @property
                @memorize
                def imgUrl(self):
                    url = self.soup.findAll('img')[1]['src']
                    return url
                @property
                def name(self):
                    hold = '{title}-{:03d}.jpg'.format(int(self.url.split('/')[-1]),
                            title=self.chapter.title)
                    return hold
