from .. import mangaSite
from ..util import memorize, webpage

tags = ['ce', 'comicextra']


class Series(mangaSite.Series):
    seriesString = 'comic/{}'
    siteTemplate = 'http://www.comicextra.com/{}'
    soupArgs = {'name': 'table', 'class_': 'table'}

    @property
    @memorize
    def chapters(self):
        return [self.Chapter(link['href'], self)
                for link in self.soup.find(**self.soupArgs)('a')[::-1]]

    def runExtras(self):
        url_search, t = self.siteTemplate.format('comic-search?key={}'), {}
        search = webpage(url_search.format(self.series.replace(' ', '+')))
        sel = search.soup(class_='cartoon-box')
        for i in sel:
            hold = i.h3.a.text
            if not hold in t.keys():
                t.update({hold: i.a['href']})
        final = t.items()
        print('Please select from the following:')
        for n, i in enumerate(final):
            print("{}: {}".format(n, i[0].encode('utf-8')))
        selection = input()
        hold = final[selection][1].split('/')[-1]
        self.series = hold
        self.title = hold

    class Chapter(mangaSite.Chapter):
        def __init__(self, link, series):
            self.url = '{}/full'.format(link)
            self.Page = series.Page
            self.series = series
            self.title = link.split('/')[-1]

        @property
        @memorize
        def pages(self):
            urls = [i['src'] for i in
                    self.soup.find(class_='chapter-container')('img')]
            return [self.Page(url, '{:03d}.jpg'.format(num))
                    for num, url in enumerate(urls)]

    class Page(mangaSite.Page):
        def __init__(self, page, name):
            self.imgUrl = page
            self.name = name
