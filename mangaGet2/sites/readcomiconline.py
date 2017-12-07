from .. import mangaSite
from ..util import memorize
from cfscrape import CloudflareScraper

tags = ['rc', 'rcbt']
session = CloudflareScraper.create_scraper()


class Series(mangaSite.Series):
    seriesString = '/Comic/{}'
    session = session
    siteTemplate = 'http://readcomiconline.to{}'
    soupArgs = {'name': 'table', 'class_': 'listing'}

    @property
    @memorize
    def chapters(self):
        return [self.Chapter('{}&readType=1'.format(link['href']), self)
                for link in self.soup(**self.soupArgs)[0]('a')][::-1]

    class Chapter(mangaSite.Chapter):
        session = session

        @property
        @memorize
        def listThem(self):
            return [i for i in self.soup('select',
                    id='selectPage')[0]('option')]
        def pages(self):
            return [self.Page(i['src'],self) for i in self.soup('div',
                    id='divImage')[0]('img')]

        @property
        @memorize
        def title(self):
            return next(sel['value'].split('?')[0] for sel in
                        self.soup.find('select', id='selectEpisode')('option')
                        if sel.has_attr('selected'))

    class Page(mangaSite.Page):
        session = session

        @property
        @memorize
        def imgUrl(self):
            url = self.soup.find('div', id='divImage').img['src']
            return url.replace(' ', '%20')

        #@property
        #def name(self):
        #    return self.imgUrl.split('/')[-1]

        @property
        @memorize
        def url(self):
            return '#'.join([self.chapter.url, self.page])
