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
        searchPage = webpage(cls.searchTemplate.format(searchString))
        searchList = searchPage.soup.find(class_=re.compile('Manga')).findParent('tbody').findAll('tr')
        dictTableList = []
        if fullTable:
            return searchList
        for i in searchList:
            them = i.findAll('td')
            try:
                lChap, dou  = them[3].text.strip('\n').split('\non ')
            except:
                lChap, dou = them[3].text.strip('\n'), ''
            name = them[0].text
            serString = them[0].a['href'].split('/')[-2]
            dictTableList.append({'name': name, 'lChap': lChap, 'dou': dou, 'serString': serString})
        return dictTableList
      
    class Series(mangaSite.Series):
        seriesString = '/en-manga/{}/'
        soupArgs = {'name': 'a', 'class_': 'chapterLink'}
        
        class Chapter(mangaSite.Series.Chapter):
            listThem = lambda self: self.soup.find('div', class_="pagination ").findAll('a', text=re.compile('[0-9]'))[1:]
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