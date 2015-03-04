import re
from mangaGet2.mangaSite import mangaSite
import mangaGet2.util as util

#Aliases
memorize = util.memorize
webpage  = util.webpage

class mangaeden(mangaSite):
    siteTemplate = 'http://www.mangaeden.com{}'
    searchTemplate = siteTemplate.format('/en-directory/?title={}')
    tags = [ 'me', 'mangaeden' ]
    
    @staticmethod
    def runSearch(searchString, fullTable=False):
        searchPage = webpage(mangaeden.searchTemplate.format(searchString))
        searchList = searchPage.soup.find(class_=re.compile('Manga')).findParent('tbody').findAll('a')
        dictTableList, newTable = [], []
        for i in range(len(searchList)/2):
            newTable.append(searchList[i*2:(i+1)*2])
        for i in newTable:
            lChap, dou  = i[1].text.split('\non ')
            name = i[0].text
            serString = i[0]['href'].split('/')[-2]
            dictTableList.append({'name': name, 'lChap': lChap, 'dou': dou, 'serString': serString})
        return dictTableList
      
    class Series(mangaSite.Series):
        seriesString = '/en-manga/{}/'
        soupArgs = {'name': 'a', 'class_': 'chapterLink'}
        
        @property
        def siteTemplate(self):
            return mangaeden.siteTemplate
        
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