from .. import mangaSite
from ..util import memorize, Util, webpage

tags = ['nh', 'nhentai']
siteTemplate = 'http://nhentai.net{}'
searchTemplate = siteTemplate.format('/search/?q=english+{}')


class Series(mangaSite.Series):
    seriesString = '/g/{}/'
    siteTemplate = 'http://nhentai.net{}'
    soupArgs = {'name': 'a', 'class_': 'chapterLink'}

    @property
    @memorize
    def chapters(self):
        return [self.Chapter(self.seriesTemplate.format(self.series), self)]

    def runExtras(self):
        self.url = searchTemplate.format(self.series)
        web = webpage(self.url)
        loop = [web]
        loop.extend([webpage(''.join([self.url, '&page=', a.text]))
                    for i in web.soup('section', class_='pagination')
                    for a in i('a')[1:-2]])
        g_list = [i.a['href'] for w in loop
                           for i in w.soup('div', class_='gallery')]
        self.chapters = [self.Chapter(self.siteTemplate.format(i), self)
                         for i in g_list]

    class Chapter(mangaSite.Chapter):
        listArgs = {'name': 'a', 'class_': 'gallerythumb'}

        def __init__(self, link, series):
            self.Page = series.Page
            self.s_temp = series.siteTemplate
            self.url = link

        @property
        @memorize
        def pages(self):
            return [self.Page(opt['href'], self)
                    for opt in self.soup(**self.listArgs)]

        @property
        def title(self):
            orig = self.soup.find('h1').text
            hold = Util.normalizeName(orig)
            return hold

    class Page(mangaSite.Page):

        @property
        @memorize
        def imgUrl(self):
            raw = self.soup.find('section', id='image-container')
            return raw.img['src']

        @property
        def name(self):
            return self.imgUrl.split('/')[-1]
