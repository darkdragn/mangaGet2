from mangaeden import mangaeden

class perveden(mangaeden):
    tags = [ 'pe', 'perveden' ]
    siteTemplate = 'http://www.perveden.com{}'
    searchTemplate = siteTemplate.format('/en-directory/?title={}')