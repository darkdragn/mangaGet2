from .. import mangaSite
from ..util import memorize

tags = ['h2r', 'hentai2read']


class Series(mangaSite.Series):
    seriesString = '{}/'
    siteTemplate = 'http://www.hentai2read.com/{}'
    soupArgs = {'name': 'table', 'class_': 'table table-hover'}

    @property
    @memorize
    def chapters(self):
        return [self.Chapter(i['href'], self) for i in self.soup.find('ul',
                class_='nav-chapters').findAll('a', class_='link-effect')]

    class Chapter(mangaSite.Chapter):
        @property
        def url(self):
            return self.link

        @property
        @memorize
        def pages(self):
            hold = ''.join([self.url, '{}/'])
            return [self.Page(hold.format(opt.text), self)
                    for opt in self.soup.find('a',
                    class_='js-rdrPage').parent.parent.findAll('a')]

        @property
        @memorize
        def title(self):
            li = self.soup.find('ol').findAll('li')[-1]
            num, title = li.span.text.split(':', 1)
            title = title.strip().replace(' ', '_').encode('utf-8')
            return '__'.join([title.replace(':', '_'),
                              num.split(' ')[-1].encode('utf-8')])

    class Page(mangaSite.Page):
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
            return self.imgUrl.split('/')[-1].split('?')[0].encode('utf-8')
