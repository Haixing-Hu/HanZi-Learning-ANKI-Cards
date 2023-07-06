# ##############################################################################
#                                                                              #
#     Copyright (c) 2023. Haixing Hu                                           #
#     All rights reserved.                                                     #
#                                                                              #
# ##############################################################################
import logging
from abc import ABC, abstractmethod
from typing import Optional

import requests
from bs4 import BeautifulSoup


class DictPage(ABC):
    """
    此模型表示指定汉字对应的字典网页页面内容。
    """
    def __init__(self, char: str) -> None:
        """
        构造函数。

        :param char: 指定的汉字。
        """
        self._char = char
        self._unicodeHex = hex(ord(char)).upper()[2:]
        self._url = self._get_page_url(char)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._soup = None

    @property
    def char(self) -> str:
        """
        获取指定的汉字。
        :return: 指定的汉字。
        """
        return self._char

    @property
    def unicodeHex(self) -> str:
        """
        获取指定汉字的Unicode编码的大写16进制表示。

        :return: 指定汉字的Unicode编码的大写16进制表示。
        """
        return self._unicodeHex

    @property
    def url(self) -> str:
        """
        获取指定汉字对应的字典网页页面的URL。

        :return: 指定汉字对应的字典网页页面的URL。
        """
        return self._url

    def get_image(self) -> Optional[str]:
        """
        获取指定汉字的图片的URL。

        :return: 该汉字的图片的URL。
        """
        if self._soup is None:
            self._soup = self._get_soup()
        result = self._get_image(self._soup)
        if result is None or result == '':
            self._logger.error('Failed to get image for character "%s": %s',
                               self._char, self._url)
        return result

    def get_pinyin(self) -> Optional[str]:
        """
        获取指定汉字的拼音。

        :return: 该汉字的拼音。
        """
        if self._soup is None:
            self._soup = self._get_soup()
        result = self._get_pinyin(self._soup)
        if result is None or result == '':
            self._logger.error('Failed to get pinyin for character "%s": %s',
                               self._char, self._url)
        return result

    def get_pronounce(self) -> Optional[str]:
        """
        获取指定汉字的读音。

        :return: 该汉字的读音音频文件的URL。
        """
        if self._soup is None:
            self._soup = self._get_soup()
        result = self._get_pronounce(self._soup)
        if result is None or result == '':
            self._logger.error('Failed to get pronounce for character "%s": %s',
                               self._char, self._url)
        return result

    def get_definitions(self) -> Optional[str]:
        """
        获取指定汉字的解释。

        :return: 该汉字的解释。
        """
        if self._soup is None:
            self._soup = self._get_soup()
        result = self._get_definitions(self._soup)
        if result is None or result == '':
            self._logger.error('Failed to get definitions for character "%s": %s',
                               self._char, self._url)
        return result

    def _get_soup(self) -> BeautifulSoup:
        """
        获取指定汉字对应的字典网页页面解析后的 BeautifulSoup 对象。

        :return: 指定汉字对应的字典网页页面解析后的 BeautifulSoup 对象。
        """
        response = requests.get(self._url)
        content = response.content
        return BeautifulSoup(content, 'html.parser')

    @abstractmethod
    def _get_page_url(self, ch) -> str:
        """
        获取指定汉字对应的字典网页页面的URL。

        :param ch: 指定的汉字。
        :return: 该汉字对应的字典网页页面的URL。
        """

    @abstractmethod
    def _get_image(self, soup: BeautifulSoup) -> Optional[str]:
        """
        获取指定汉字的图片的URL。

        :param soup: 解析后的指定汉字对应的字典网页页面内容。
        :return: 该汉字的图片的URL。
        """

    @abstractmethod
    def _get_pinyin(self, soup: BeautifulSoup) -> Optional[str]:
        """
        获取指定汉字的拼音。

        :param soup: 解析后的指定汉字对应的字典网页页面内容。
        :return: 该汉字的拼音。
        """

    @abstractmethod
    def _get_pronounce(self, soup: BeautifulSoup) -> Optional[str]:
        """
        获取指定汉字的读音。

        :param soup: 解析后的指定汉字对应的字典网页页面内容。
        :return: 该汉字的读音音频文件的URL。
        """

    @abstractmethod
    def _get_definitions(self, soup: BeautifulSoup) -> Optional[str]:
        """
        获取指定汉字的释义。

        :param soup: 解析后的指定汉字对应的字典网页页面内容。
        :return: 该汉字的释义。
        """
