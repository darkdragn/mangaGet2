from ..mangaSite import Chapter, Page, Series
from ..util import memorize

tags = ['mp', 'mangapark']


class Series(Series):
    siteTemplate = 'http://www.mangapark.com{}'
    seriesString = '/manga/{}/'
    soupArgs = {'name': 'div', 'class_': 'stream'}
    version = 0

    @property
    @memorize
    def chapters(self):
        soup_bowl = self.soup.findAll(**self.soupArgs)[self.version]
        return [self.Chapter(tag.find(text='all').parent['href'], self)
                for tag in soup_bowl.findAll('em')[::-1]]

    def runExtras(self):
        for i in self.extras.split(','):
            if 'ver' in i:
                self.version = int(i.split('=')[-1])-1

    class Chapter(Chapter):
        @property
        def listThem(self):
            return [{'value': i['src']}
                    for i in self.soup.findAll('img', class_='img')]

        def pageCut(self, curString):
            if 'blank' in curString['src']:
                return curString['data-original']
            else:
                return curString['src']

        @property
        def title(self):
            hold = self.url.split('/')[-2:]
            hold[0] = ''.join(['v', '{:0>2}'.format(hold[0].strip('v'))])
            hold[-1] = hold[-1].strip('c')
            if '.' in hold[-1]:
                hold[-1] = '{:0>3}.{:0>2}'.format(*hold[-1].split('.'))
            else:
                hold[-1] = '{:0>3}'.format(hold[-1])
            if 's' not in hold[0]:
                return '_'.join(hold)
            return hold[-1]

    class Page(Page):
        @property
        def imgUrl(self):
            return self.page

        @property
        def name(self):
            hold = self.imgUrl.split('/')[-1].split('.')
            return '.'.join(['{:0>3}'.format(hold[0]), hold[1].split('?')[0]])
