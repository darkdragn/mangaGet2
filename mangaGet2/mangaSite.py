from util import memorize, webpage


class Series(webpage):
    soupArgs = NotImplemented

    def __init__(self, series, extras=None, site=None):
        self.extras = extras
        self.series = series
        self.title = series
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
        return [self.Chapter(link['href'], self)
                for link in self.soup.findAll(**self.soupArgs)[::-1]]

    @property
    def seriesTemplate(self):
        return self.siteTemplate.format(self.seriesString)

    @property
    @memorize
    def url(self):
        return self.seriesTemplate.format(self.series)


class Chapter(webpage):

    def __init__(self, link, series):
        self.link = link
        self.Page = series.Page
        self.series = series
        self.s_temp = series.siteTemplate

    @property
    def listThem(self):
        return self.soup.find(**self.listArgs).findChildren()

    @property
    @memorize
    def pages(self):
        return [self.Page(opt['value'], self)
                for opt in self.listThem]

    @property
    def title(self):
        return

    @property
    @memorize
    def url(self):
        return self.s_temp.format(self.link)


class Page(webpage):
    picCompile = NotImplemented

    def __init__(self, page, chapter):
        self.chapter = chapter
        self.cookie = chapter.cookie
        self.page = page
        self.s_temp = chapter.s_temp

    @property
    def image(self):
        return Image(self.imgUrl, self.name)

    @property
    def name(self):
        return

    @property
    @memorize
    def url(self):
        return self.s_temp.format(self.page)


class Image():

    def __init__(self, url, nameIt=None):
        self.nameIt = nameIt
        self.url = url
