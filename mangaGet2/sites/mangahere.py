from ..mangaSite import Chapter, Page, Series
from ..util import memorize

tags = ['mh', 'mangahere']


class Series(Series):
    seriesString = 'manga/{}/'
    siteTemplate = 'http://www.mangahere.co/{}'
    soupArgs = {'name': 'div', 'class_': 'detail_list'}

    @property
    @memorize
    def chapters(self):
        soup_table = self.soup.find(**self.soupArgs).findAll('a')
        return [self.Chapter(link['href'], self)
                for link in soup_table][::-1]

    class Chapter(Chapter):
        @property
        @memorize
        def pages(self):
            soup_table = self.soup.find('select', class_='wid60')
            return [self.Page(opt['value'], self)
                    for opt in soup_table.findAll('option')]

        @property
        @memorize
        def title(self):
            return self.url.split('/')[-2]

        @property
        @memorize
        def url(self):
            return self.link

    class Page(Page):
        @property
        @memorize
        def imgUrl(self):
            return self.soup.find('img', id='image')['src']

        @property
        def name(self):
            return self.imgUrl.split('/')[-1].split('?')[0]

        @property
        @memorize
        def url(self):
            return self.page
