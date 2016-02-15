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
        seriesString = '{}/1/'
        siteTemplate = 'http://www.hentai2read.com/{}'
        soupArgs = {'name': 'table', 'class_': 'table table-hover'}
        
        @property
        def chapters(self):
            chapTemp = ''.join([self.siteTemplate.format(self.series), '/{}/'])
            return [self.Chapter(chapTemp.format(i['value']), self) 
                    for i in self.soup.find('select',
                        class_='cbo_wpm_chp').findAll('option')][::-1]
        class Chapter(mangaSite.Series.Chapter):
            @property
            def url(self):
                return self.link
            @property
            @memorize
            def pages(self):
                hold = ''.join([self.url, '{}/'])
                return [self.Page(hold.format(opt['value']), self)
                        for opt in self.soup.find('select',
                        class_='cbo_wpm_pag').findAll('option')]
            @property
            @memorize
            def title(self):
                return self.soup.h1.text.split('>')[-1].replace(u'\u2019',
                        '\'')
            class Page(mangaSite.Series.Chapter.Page):
                @property
                def url(self):
                    return self.page
                @property
                @memorize
                def imgUrl(self):
                    return self.soup.find('div', class_='prw').img['src']
                @property
                def name(self):
                    return self.imgUrl.split('/')[-1]
