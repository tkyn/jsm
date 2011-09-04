# coding=utf-8
#---------------------------------------------------------------------------
# Copyright 2011 utahta
#---------------------------------------------------------------------------
import urllib2
import math
import time
from jsm.util import html_parser
from jsm.brand import BrandData

class SearchParser(object):
    """銘柄検索ページパーサ"""
    SITE_URL = "http://stocks.finance.yahoo.co.jp/stocks/search/?s=%(terms)s&p=%(page)s&ei=UTF-8"
    DATA_FIELD_NUM = 7 # データの要素数
    COLUMN_NUM = 50 # 1ページ辺り最大行数

    def __init__(self):
        self._elms = []
        self._max_page = 0
    
    def fetch(self, terms, page=1):
        """銘柄検索結果を取得
        terms: 検索ワード
        page: ページ
        """
        siteurl = self.SITE_URL % {'terms':terms, 'page':page}
        fp = urllib2.urlopen(siteurl)
        html = fp.read()
        fp.close()
        soup = html_parser(html)
        # 全件数
        elm = soup.find('div', {'class': 'ymuiPagingTop yjSt marB4 clearFix'})
        self._max_page = int(math.ceil(int(self._text(elm)) / 50.0))
        # データ
        elm = soup.find("div", {'class': 'boardFinList fsize13px s130 marB10'})
        self._elms = elm.findAll('tr')
        
    def fetch_all(self, terms, page=1):
        """検索結果を全部取得
        """
        elms = []
        self.fetch(terms, page)
        elms.extend(self._elms)
        for page in xrange(2, self._max_page+1):
            self.fetch(terms, page)
            elms.extend(self._elms)
            time.sleep(0.5)
        self._elms = elms
        
    def get(self):
        result_set = []
        for elm in self._elms:
            tds = elm.findAll('td')
            if tds:
                market = self._market(tds[1])
                if market:
                    res = BrandData(self._text(tds[0]), 
                                    market,
                                    self._text(tds[2]),
                                    '')
                    result_set.append(res)
        return result_set
    
    def _market(self, soup):
        return soup.text.encode('utf-8')
    
    def _text(self, soup):
        strong = soup.find("strong")
        if strong:
            return strong.text.encode("utf-8")
        else:
            return ""

class Search(object):
    """銘柄検索
    """
    def get(self, terms):
        p = SearchParser()
        p.fetch_all(terms)
        return p.get()
        