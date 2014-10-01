import scrapy

from scrapy.dupefilter import RFPDupeFilter

class SeenURLFilter(RFPDupeFilter):
    """A dupe filter that considers the URL"""

    '''
    def __init__(self):
        self.urls_seen = set()
        RFPDupeFilter.__init__(self, path)
    '''

    def request_seen(self, request):
        if request.url in self.fingerprints:
            return True
        else:
            self.fingerprints.add(request.url)
