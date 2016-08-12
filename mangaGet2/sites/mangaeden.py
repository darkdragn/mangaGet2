import re
from mangaGet2.mangaSite import mangaSite
import mangaGet2.util as util

#Aliases
memorize = util.memorize
webpage  = util.webpage

class mangaeden(mangaSite):
    tags = [ 'me', 'mangaeden' ]
    siteTemplate = 'http://www.mangaeden.com{}'
    searchTemplate = siteTemplate.format('/en-directory/?title={}')
    
    @classmethod
    def runSearch(cls, searchString, fullTable=False):
        search_page = webpage(cls.searchTemplate.format(searchString))
        search_table= search_page.soup.find(class_=re.compile('Manga'))
        search_list = search_table.findParent('tbody').findAll('tr')
        dictTableList = []
        if fullTable:
            return search_list
        for i in search_list:
            them = i.findAll('td')
            try:
                lChap, dou  = them[3].text.strip('\n').split('\non ')
            except:
                lChap, dou = them[3].text.strip('\n'), ''
            name = them[0].text
            serString = them[0].a['href'].split('/')[-2]
            dictTableList.append({'name': name, 'lChap': lChap, 'dou': dou, 
                'serString': serString})
        return dictTableList
      
    class Series(mangaSite.Series):
        seriesString = '/en-manga/{}/'
        siteTemplate = 'http://www.mangaeden.com{}'
        soupArgs = {'name': 'a', 'class_': 'chapterLink'}
        
        class Chapter(mangaSite.Series.Chapter):
            def listThem(self):
                hold = self.soup.find_all('select', class_="selected")[1]
                return hold.find_all('option')
            @property
            @memorize
            def pages(self):
                hold = [self.Page(self.link, self)]
                for i in self.listThem():
                    hold.append(self.Page(i['value'], self))
                return hold
            @property
            def title(self):
                orig = self.url.split('/')[-3]
                padIt = lambda x: '{:0>3}'.format(int(x))
                if '.' in orig:
                    hold = orig.split('.')
                    return '.'.join([padIt(hold[0]), hold[1]])
                return padIt(orig)
            class Page(mangaSite.Series.Chapter.Page):
                @property
                @memorize
                def imgUrl(self):
                    raw = self.sour.find('img', id='mainImg')
                    return 'http:{}'.format(raw['src'])
                @property
                def name(self):
                    return '.'.join(['{:0>3}'.format(self.page.split('/')[-2]), 
                                     self.imgUrl.split('.')[-1]])
