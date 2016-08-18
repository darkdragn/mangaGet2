from .. import mangaSite
from ..util import memorize

tags = ['me', 'mangaeden']
siteTemplate = 'http://www.mangaeden.com{}'
searchTemplate = siteTemplate.format('/en-directory/?title={}')


class Series(mangaSite.Series):
    seriesString = '/en-manga/{}/'
    siteTemplate = 'http://www.mangaeden.com{}'
    soupArgs = {'name': 'a', 'class_': 'chapterLink'}

    class Chapter(mangaSite.Chapter):
        listArgs = {'name': 'select', 'id': 'pageSelect'}

        @property
        def title(self):
            orig = self.url.split('/')[-3]
            hold = orig.split('.')
            hold[0] = '{:03}'.format(int(hold[0]))
            return '.'.join(hold)

    class Page(mangaSite.Page):
        @property
        @memorize
        def imgUrl(self):
            raw = self.soup.find('img', id='mainImg')
            return 'http:{}'.format(raw['src'])

        @property
        def name(self):
            return '.'.join(['{:0>3}'.format(self.page.split('/')[-2]),
                             self.imgUrl.split('.')[-1]])
