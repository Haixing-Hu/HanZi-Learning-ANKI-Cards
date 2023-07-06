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


class ZdicDictPage(DictPage):
    """
    此模型表示指定汉字对应的汉典页面内容。
    """
    def _get_page_url(self, ch) -> str:
        return f'https://www.zdic.net/hans/{quote(ch)}'

    def _get_image(self, soup: BeautifulSoup) -> Optional[str]:
        return f'https://img.zdic.net/kai/jbh/{self._unicodeHex}.gif'

    def _get_pinyin(self, soup: BeautifulSoup) -> Optional[str]:
        pinyin_element = soup.select_one('span.dicpy')
        if pinyin_element:
            pinyin_text = pinyin_element.contents[0].text.strip().split()[0]
            return pinyin_text
        return None

    def _get_pronounce(self, soup: BeautifulSoup) -> Optional[str]:
        pronounce_element = soup.select_one('.dicpy > .ptr > .audio_play_button')
        if pronounce_element:
            url = pronounce_element.attrs['data-src-mp3']
            return f'https:{url}'
        return None

    def _get_definitions(self, soup: BeautifulSoup) -> Optional[str]:
        definitions_element = soup.select_one('.content.definitions.jnr > ol')
        if definitions_element:
            definitions = []
            for index, li in enumerate(definitions_element.find_all('li'), 1):
                definition = li.text\
                    .replace('～', self._char)\
                    .strip()
                definitions.append(f"{index}. {definition}")
            if len(definitions) == 0:
                for index, li in enumerate(definitions_element.find_all('p'), 1):
                    definition = li.text\
                        .replace('◎', '')\
                        .replace('～', self._char)\
                        .strip()
                    definitions.append(f"{index}. {definition}")
            return '<br>'.join(definitions)
        return None
