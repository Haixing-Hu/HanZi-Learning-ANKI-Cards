# ##############################################################################
#                                                                              #
#     Copyright (c) 2023. Haixing Hu                                           #
#     All rights reserved.                                                     #
#                                                                              #
# ##############################################################################
from typing import Optional
from urllib.parse import quote

from bs4 import BeautifulSoup

from dict_page import DictPage


class BaiduDictPage(DictPage):
    """
    此模型表示指定汉字对应的百度汉语页面内容。
    """
    def _get_page_url(self, ch) -> str:
        return f'https://dict.baidu.com/s?wd={quote(ch)}&ptype=zici'

    def _get_image(self, soup: BeautifulSoup) -> Optional[str]:
        return f'https://img.zdic.net/kai/jbh/{self._unicodeHex}.gif'

    def _get_pinyin(self, soup: BeautifulSoup) -> Optional[str]:
        pinyin_element = soup.select_one('#pinyin > span > b')
        if pinyin_element:
            return pinyin_element.text
        return None

    def _get_pronounce(self, soup: BeautifulSoup) -> Optional[str]:
        pronounce_element = soup.select_one('.mp3-play')
        if pronounce_element:
            return pronounce_element.attrs['url']
        return None

    def _get_definitions(self, soup: BeautifulSoup) -> Optional[str]:
        definitions_elements = soup.select('#basicmean-wrapper > .tab-content > dl > dd > p')
        if definitions_elements:
            definitions = []
            for p in definitions_elements:
                definition = p.text.strip().replace('～', self._char)
                definitions.append(definition)
            return '<br>'.join(definitions)
        return None
