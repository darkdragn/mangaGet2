from .. import mangaSite
from ..util import memorize

tags = ['cc', 'comicastle']


class Series(mangaSite.Series):
    seriesString = 'manga-{}.html'
    siteTemplate = 'http://www.comicastle.org/{}'
    soupArgs = {'name': 'table', 'class_': 'table table-hover'}

    @property
    @memorize
    def chapters(self):
        return [self.Chapter(link['href'], self)
                for link in self.soup.find(**self.soupArgs).findAll('a')]

    class Chapter(mangaSite.Chapter):
        @property
        @memorize
        def listThem(self):
            return self.soup.findAll('select')[1].findChildren()[:-1]

        @property
        @memorize
        def title(self):
            hold = self.soup.findAll('select')[0]
            out = hold.find(lambda tag: tag.has_attr('selected')).text
            return out.strip()

    class Page(mangaSite.Page):
        @property
        @memorize
        def imgUrl(self):
            url = self.soup.find('img', class_='chapter-img')['src']
            return url.strip(' \n').strip().replace(' ', '%20')

        @property
        def name(self):
            return self.imgUrl.split('/')[-1]
