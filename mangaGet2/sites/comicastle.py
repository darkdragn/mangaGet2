import re
from mangaGet2.mangaSite import mangaSite
import mangaGet2.util as util

#Aliases
memorize = util.memorize
webpage  = util.webpage

class comicastle(mangaSite):
    tags = [ 'cc', 'comicastle' ]
    
    class Series(mangaSite.Series):
        seriesString = 'manga-{}.html'
        siteTemplate = 'http://www.comicastle.org/{}'
        soupArgs = {'name': 'table', 'class_': 'table table-hover'}
        
        @property
        @memorize
        def chapters(self):
            return [self.Chapter(link['href'], self) 
                    for link in self.soup.find(**self.soupArgs).findAll('a')]
        class Chapter(mangaSite.Series.Chapter):
            @property
            @memorize
            def pages(self):
                return [self.Page(opt['value'], self)
                        for opt in self.soup.findAll('select')[1].findAll('option')[:-1]]
            @property
            @memorize
            def title(self):
                sel  = lambda tag: tag.has_attr('selected')
                hold = self.soup.findAll('select')[0].find(sel).text
                return hold.strip()
            class Page(mangaSite.Series.Chapter.Page):
                @property
                @memorize
                def imgUrl(self):
                    url = self.soup.find('img', class_='chapter-img')['src']
                    return url.strip(' \n').strip().replace(' ', '%20')
                @property
                def name(self):
                    return self.imgUrl.split('/')[-1]
