from .. import mangaSite
from ..util import memorize

tags = ['rcbo', 'rcb']


class Series(mangaSite.Series):
    seriesString = '{}'
    siteTemplate = 'http://readcomicbooksonline.me/{}'
    soupArgs = {'name': 'div', 'id': 'chapterlist'}

    @property
    @memorize
    def chapters(self):
        hold = [self.Chapter(link['href'], self)
                for link in self.soup.find(**self.soupArgs).findAll('a')][::-1]
        if 'ongoing' in self.soup('td', class_='info')[-1].text:
            return hold[:-1]
        return hold


    class Chapter(mangaSite.Chapter):
        @property
        @memorize
        def listThem(self):
            return self.soup.findAll('select')[-1]('option')

        @property
        @memorize
        def title(self):
            # hold = self.soup.find('div', class_='backtag')('a')[-1].text
            hold = [i['value'] for i in self.soup('option')
                    if i.has_attr('selected')][0]
            return hold.replace(' ', '_')

        @property
        @memorize
        def url(self):
            return self.link

    class Page(mangaSite.Page):
        @property
        @memorize
        def imgUrl(self):
            hold = self.soup.find('img', class_='picture')['src']
            url = self.s_temp.format('/'.join(['reader', hold]))
            return url.replace(' ', '%20')

        @property
        def name(self):
            return self.imgUrl.split('/')[-1]

        @property
        @memorize
        def url(self):
            return '/'.join([self.chapter.url, self.page])
