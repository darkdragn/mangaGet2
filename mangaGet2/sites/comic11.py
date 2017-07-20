from .. import mangaSite
from ..util import memorize, webpage

tags = ['11c', '11', '11comic']


class Series(mangaSite.Series):
    seriesString = '/comic/{}'
    siteTemplate = 'http://www.11comic.com{}'

    def __init__(self, series, extras=None, site=None):
        self.extras = extras
        self.series = series
        if self.extras:
            self.runExtras()
        if site:
            try:
                self.siteTemplate = site.siteTemplate
            except AttributeError:
                pass

    @property
    @memorize
    def chapters(self):
        links = self.soup('section', class_='issues')[0]('li')[::-1]
        return [self.Chapter(self.siteTemplate.format(i.a['href']), self, num)
                for num, i in enumerate(links, 1)]
    def runExtras(self):
        self.num_title = True

    @property
    @memorize
    def title(self):
        return self.soup.h1.text.replace(' ', '_')

    class Chapter(mangaSite.Chapter):
        def __init__(self, link, series, num):
            self.url = '{}full.html'.format(link)
            self.num = num
            self.Page = series.Page
            self.series = series

        @property
        @memorize
        def title(self):
            if hasattr(self.series, 'num_title'):
                return '_'.join([self.series.title, str(self.num)])
            obj = self.soup('section', class_='d_title')[0]
            return obj.text.split('/')[1].strip().replace(' ', '_')
        @property
        @memorize
        def pages(self):
            urls = [i['src'] for i in self.soup('img')[1:]]
            return [self.Page(url, '{:03d}.jpg'.format(num), self)
                    for num, url in enumerate(urls)]

    class Page(mangaSite.Page):
        def __init__(self, page, name, chapter):
            self.chapter = chapter
            self.imgUrl = page
            self.name = name
