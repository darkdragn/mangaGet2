import re
from mangaGet2.mangaSite import mangaSite
import mangaGet2.util as util

#Aliases
memorize = util.memorize
webpage  = util.webpage

class hentai2read(mangaSite):
    tags = [ 'h2r', 'hentai2read' ]
    #defaults = {'top': False}
    
    class Series(mangaSite.Series):
        seriesString = '{}/'
        siteTemplate = 'http://www.hentai2read.com/{}'
        soupArgs = {'name': 'table', 'class_': 'table table-hover'}
        
        @property
        def chapters(self):
            chapTemp = ''.join([self.siteTemplate.format(self.series), '/{}/'])
            with open('test', 'ab') as f:
                for line in self.source:
                    f.write(line)
            return [self.Chapter(i['href'], self) for i in self.soup.find('ul',
                class_='nav-chapters').findAll('a', class_='link-effect')]
        class Chapter(mangaSite.Series.Chapter):
            @property
            def url(self):
                return self.link
            @property
            @memorize
            def pages(self):
                hold = ''.join([self.url, '{}/'])
                return  [self.Page(hold.format(opt.text), self)
                        for opt in self.soup.find('a',
                        class_='js-rdrPage').parent.parent.findAll('a')]
            @property
            @memorize
            def title(self):
                li = self.soup.find('ol').findAll('li')[-1]
                return li.span.text.replace(' ', '_')
            class Page(mangaSite.Series.Chapter.Page):
                @property
                def url(self):
                    return self.page
                @property
                @memorize
                def imgUrl(self):
                    url = self.soup.find('img', id='arf-reader')['src']
                    return ''.join(['http:', url])
                @property
                def name(self):
                    return self.imgUrl.split('/')[-1].split('?')[0]
