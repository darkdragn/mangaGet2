import re
from mangaGet2.mangaSite import mangaSite
import mangaGet2.util as util

#Aliases
memorize = util.memorize
webpage  = util.webpage

class mangapark(mangaSite):
    searchTemplate = 'http://www.mangapark.com/search?q={}'
    siteTemplate = 'http://www.mangapark.com{}'
    tags = ['mp', 'mangapark']
    
    @staticmethod
    def runSearch(searchString, fullTable=False):
        searchPage = webpage(mangapark.searchTemplate.format(searchString))
        searchTable = searchPage.soup.findAll('table')[1:]
        dictTableList = []
        for i in searchTable:
            dou    = i.h3.i.text
            lChap  = i.h3.b.text
            name   = i.tr.td.a['title']
            serString = i.tr.td.a['href'].split('/')[-1]
            dictTableList.append({'name': name, 'lChap': lChap, 'dou': dou, 'serString': serString})
        return dictTableList
    
    class Series(mangaSite.Series):
        seriesString = '/manga/{}/'
        soupArgs = {'name': 'div', 'class_': 'stream'}
        version = 0
        
        @property
        @memorize
        def chapters(self):
            return [self.Chapter(tag.find(text='all').parent['href'], self) 
                    for tag in self.soup.findAll(**self.soupArgs)[self.version].findAll('em')[::-1]]
        def runExtras(self):
            for i in self.extras.split(','):
                if 'ver' in i:
                    self.version = int(i.split('=')[-1])-1
        
        class Chapter(mangaSite.Series.Chapter):
            listThem = lambda self: self.soup.findAll('img', class_='img')
            @property
            @memorize
            def pages(self):
                return [self.Page(i['src'].split('?')[0], self) for i in self.listThem()]
            @property
            def title(self):
                hold = self.url.split('/')[-2:]
                hold[0] = ''.join(['v', '{:0>2}'.format(hold[0].strip('v'))])
                hold[-1] = hold[-1].strip('c')                                                                                                                                            
                if '.' in hold[-1]:
                    hold[-1] = '{:0>3}.{:0>2}'.format(*hold[-1].split('.'))
                else:
                    hold[-1] = '{:0>3}'.format(hold[-1])
                if not 's' in hold[0]:
                    return '_'.join(hold)
                return hold[-1]
            
            class Page(mangaSite.Series.Chapter.Page):
                @property
                def imgUrl(self):
                    return self.page
                @property
                def name(self):
                    hold = self.imgUrl.split('/')[-1].split('.')
                    return '.'.join(['{:0>3}'.format(hold[0]), hold[1]])
