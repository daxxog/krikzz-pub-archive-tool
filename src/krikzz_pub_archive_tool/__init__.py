from __future__ import annotations
from typing import (
    List,
    Union,
    Optional
)
from functools import cached_property
from os import (
    mkdir,
    environ
)
from os.path import (
    dirname,
    basename,
    join as path_join,
)
from urllib.parse import unquote
from tempfile import TemporaryDirectory
from tarfile import open as tarfile_open

from requests import (
    Response,
    get as requests_get
)
from bs4 import (
    BeautifulSoup,
    Tag
)


from logging import (
    getLogger,
    basicConfig as logging_basicConfig,
    NOTSET as loglevel_NOTSET,
    DEBUG as loglevel_DEBUG,
    INFO as loglevel_INFO,
    WARNING as loglevel_WARNING,
    ERROR as loglevel_ERROR,
    CRITICAL as loglevel_CRITICAL
)
__LOGLEVELS__ = {
    'NOTSET': loglevel_NOTSET,
    'DEBUG': loglevel_DEBUG,
    'INFO': loglevel_INFO,
    'WARNING': loglevel_WARNING,
    'ERROR': loglevel_ERROR,
    'CRITICAL': loglevel_CRITICAL
}
__LOGLEVEL__ = environ.get('KPAT_LOGLEVEL', 'INFO')
logging_basicConfig(level=__LOGLEVELS__[__LOGLEVEL__])
log = getLogger(__name__)


__SITE_INDEX__ = 'https://krikzz.com/'
__SCRAPER_INDEX__ = __SITE_INDEX__ + 'pub/'
__SCRAPER_ICONS__ = __SITE_INDEX__ + 'ico/'
__OUTPUT_FILE__ = 'krikzz-pub-archive.tar.gz'


class ScrapeObject:
    url: str
    _response: Response

    def __init__(self, url: str, response: Response = None):
        self.url: str = url
        self._response: Response = response

    def _do_request(self) -> Response:
        log.info("request made: " + self.url)
        return requests_get(self.url)

    @cached_property
    def response(self) -> Response:
        return self._response if self._response else self._do_request()

    @cached_property
    def is_html(self) -> bool:
        return (
            self.response.status_code == 200 and
            'Content-Type' in self.response.headers and
            'text/html' in self.response.headers['Content-Type']
        )

    @cached_property
    def path(self) -> str:
        _path = self.url.replace(__SITE_INDEX__, '')
        _dir = dirname(_path)
        _base = unquote(basename(_path))

        return path_join(_dir, _base)


class ScrapeFolder(ScrapeObject):
    @cached_property
    def html(self) -> str:
        if self.response.status_code == 200:
            return self.response.text
        else:
            raise Exception(f'Non 200 status code from {self.url}, got {r.status_code} !')

    @cached_property
    def soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.html, 'html.parser')

    @cached_property
    def links(self) -> List[str]:
        return list(
            filter(
                lambda href: ('?' not in href),
                map(
                    lambda tag: tag['href'],
                    filter(
                        lambda tag: (not tag.string == 'Parent Directory'),
                        self.soup.find_all('a')
                    )
                )
            )
        )

    @cached_property
    def ls(self) -> List[Union[ScrapeObject, 'ScrapeFolder']]:
        _list = []

        for link in self.links:
            url = self.url + link
            obj = ScrapeObject(url)
            if obj.is_html:
                obj = ScrapeFolder(url, response=obj.response)

            _list.append(obj)

        return _list


class Scraper:
    index: ScrapeFolder
    temp_dir: TemporaryDirectory

    def __init__(self,
        index = ScrapeFolder(__SCRAPER_INDEX__),
        temp_dir: Optional[TemporaryDirectory] = None
    ):
        self.index = index
        self.temp_dir = temp_dir

    def scrape(self):
        with TemporaryDirectory() as temp_dir:
            self.temp_dir = temp_dir

            # scrape icons
            _index = self.index
            self.index = ScrapeFolder(__SCRAPER_ICONS__)
            self._scrape()

            # scrape everything else
            self.index = _index
            self._scrape()

            # save the contents of the temp directory to a tar
            log.info(f'saving tar: {__OUTPUT_FILE__}')
            with tarfile_open(__OUTPUT_FILE__, 'w:gz') as tar:
                tar.add(self.temp_dir, arcname='.')

    def _scrape(self):
        # create the directory to save the index
        path = path_join(self.temp_dir, self.index.path)
        mkdir(path)

        # save the index
        path = path_join(path, 'index.html')
        self._save(self.index, path)

        # iterate through objects in the index
        for obj in self.index.ls:
            if type(obj) == ScrapeFolder:
                # if the object is a folder, use recursion to scrape it
                s = Scraper(obj, self.temp_dir)
                s._scrape()
            else:
                # find this object's path
                path = path_join(self.temp_dir, obj.path)

                # save the object
                self._save(obj, path)

    def _save(self, obj, path):
        log.debug('saving to: ' + path)
        with open(path, 'wb') as f:
            f.write(obj.response.content)


def main():
    s: Scraper = Scraper()
    s.scrape()
