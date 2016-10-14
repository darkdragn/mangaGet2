import os
import requests
import shutil
import sites

from .util import display, mkparentdir, threadIt, writeStats, zipItUp

site_list = [getattr(sites, name) for name in sites.__all__]


class main():
    def __init__(self, series, site=site_list[0], chap=None, chapLast=None,
                 extras=None, search=None, top=True, thread=4):
        self.site, self.seriesStr = site, series
        self.chapl, self.top = chapLast, top
        self.extras, self.threads = extras, thread
        self.series = self.searchIt() if search \
            else site.Series(series, extras, site)
        self.downChapThread(self.series.chapters[chap-1]) if chap \
            else self.downSeries()

    @staticmethod
    def downImage(page, dir=None):
        while True:
            try:
                writeName = page.name
                if dir:
                    writeName = '/'.join([dir, writeName])
                if os.path.exists(writeName):
                    return
                img = requests.get(page.image.url,
                                   headers={'referer': page.chapter.url})
                if not img.status_code == 200:
                    pass
                with open(writeName, 'wb') as f:
                    f.write(img.content)
                break
            except AttributeError:
                raise
                break

    def downChapThread(self, chapter, dirIt=None):
        global thread
        baseName = '/'.join([dirIt, chapter.title]) if dirIt else chapter.title
        zipName = '.'.join([baseName, 'cbz'])
        if os.path.exists(zipName):
            return
        mkparentdir(baseName)
        writeStats(chapter, baseName)
        if self.threads == 1:
            start = next(len(i[2])-1 for i in os.walk(baseName))
            start = start if start >= 0 else 0
            for i in chapter.pages[start:]:
                try:
                    self.downImage(i, baseName)
                except TypeError:
                    with open('test', 'wb') as f:
                        f.write(i.source)
        else:
            thread = threadIt(self.downImage, chapter.pages, baseName,
                              self.threads)
            thread.run()
        zipItUp(zipName)
        shutil.rmtree(baseName)

    def downSeries(self):
        title = self.series.title
        if self.top:
            mkparentdir(title)
        total = self.chapl if self.chapl else len(self.series.chapters)
        display('\nSeries {name} contains {num} chapters.\n'.format(name=title,
                                                                    num=total))
        chapList = self.series.chapters[-self.chapl:] if self.chapl \
            else self.series.chapters
        for cur, chap in enumerate(chapList, 1):
            ticker = '\r[{:-<10}] Raw:'.format(('+' * ((cur)*10/total)))
            status = '{}/{}    Chapter Name: {}'.format(cur, total, chap.title)
            display(' '.join([ticker, status]), 1, 1)
            self.downChapThread(chap, title if self.top else None)
        display('\n')
