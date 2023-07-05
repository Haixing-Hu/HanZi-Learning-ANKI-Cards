# ==============================================================================
#                                                                              =
#    Copyright (c) 2023. Haixing Hu                                            =
#    All rights reserved.                                                      =
#                                                                              =
# ==============================================================================
import os
import sys
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from typing import List, Dict, Set


def get_unicode_hex(ch: str) -> str:
    """
    获取指定汉字的Unicode编码的大写16进制表示。

    :param ch: 指定的汉字。
    :return: 指定汉字的Unicode编码的大写16进制表示。
    """
    return hex(ord(ch)).upper()[2:]


def get_image(ch: str) -> str:
    """
    获取指定汉字的笔顺图URL。

    :param ch: 指定的汉字。
    :return: 该汉字的笔顺图URL。
    """
    code = get_unicode_hex(ch)
    return f'https://img.zdic.net/kai/jbh/{code}.gif'


def get_dict_page_content(ch: str) -> bytes:
    """
    获取指定的汉字对应的百度汉语页面内容。

    :param ch: 指定的汉字。
    :return: 该汉字对应的百度汉语页面内容。
    """
    url = f'https://dict.baidu.com/s?wd={quote(ch)}&ptype=zici'
    response = requests.get(url)
    return response.content


def get_pinyin(soup: BeautifulSoup) -> str:
    """
    从百度汉语页面中抽取汉字的拼音。

    :param soup: 解析后的百度汉语页面对象。
    :return: 该汉字的拼音。
    """
    pinyin_element = soup.select_one('#pinyin > span > b')
    if pinyin_element:
        return pinyin_element.text
    return ''


def get_pronounce(soup: BeautifulSoup) -> str:
    """
    从百度汉语页面中抽取汉字的发音。

    :param soup: 解析后的百度汉语页面对象。
    :return: 该汉字的发音的mp3文件的链接。
    """
    pronounce_element = soup.select_one('.mp3-play')
    if pronounce_element:
        return pronounce_element.attrs['url']
    return ''


def get_definitions(soup: BeautifulSoup, char: str) -> str:
    """
    从百度汉语页面中抽取汉字的解释。

    :param soup: 解析后的百度汉语页面对象。
    :param char: 指定的汉字。
    :return: 对该汉字的解释。
    """
    definitions_elements = soup.select('#basicmean-wrapper > .tab-content > dl > dd > p')
    if definitions_elements:
        definitions = []
        for p in definitions_elements:
            definition = p.text.strip().replace('～', char)
            definitions.append(definition)
        return '<br>'.join(definitions)
    return ''


def collect_characters(input_files: List[str]) -> Dict[str, Set[str]]:
    """
    收集所有待制作卡片的汉字及其标签。

    :param input_files: 输入文件的文件名列表。
    :return: 包含所有汉字及其对应的标签的字典。
    """
    result = {}
    for input_file in input_files:
        print(f'Processing input file: {input_file}')
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            book_name = os.path.splitext(os.path.basename(input_file))[0]
            chapter_name = ''
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    chapter_name = line[1:].strip()
                elif line:
                    tag = f'{book_name}{chapter_name}'
                    chars = [c.strip() for c in line.split('、') if c.strip()]
                    total = len(chars)
                    current = 0
                    for c in chars:
                        current += 1
                        if c in result:
                            result[c].add(tag)
                        else:
                            result[c] = {tag}
                        print(f'Reading character {current}/{total}: {c} [{tag}]')
    return result


def generate_cards(characters: Dict[str, Set[str]], output_file: str):
    """
    生成Anki卡片表格数据并将其写入输出文件。

    :param characters: 包含现有汉字及其对应标签的字典
    :param output_file: 输出文件名。
    """
    total = len(characters)
    current = 0
    with open(output_file, 'w', encoding='utf-8') as file:
        for ch, tags in characters.items():
            current += 1
            content = get_dict_page_content(ch)
            soup = BeautifulSoup(content, 'html.parser')
            image = get_image(ch)
            pinyin = get_pinyin(soup)
            pronounce = get_pronounce(soup)
            definitions = get_definitions(soup, ch)
            tags_str = ' '.join(tags)
            line = f'{tags_str} | {ch} | {pinyin} | {definitions} | {image} | {pronounce}\n'
            file.write(line)
            progress = current / total * 100
            print(f'Processing character {current}/{total} - Progress: {progress:.2f}% : {ch} [{tags_str}]')


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 pinyin_dict.py input_file1 input_file2 ... output_file")
        return

    input_files = sys.argv[1:-1]
    output_file = sys.argv[-1]

    # 删除已存在的输出文件
    if os.path.exists(output_file):
        os.remove(output_file)

    characters = collect_characters(input_files)
    generate_cards(characters, output_file)


if __name__ == '__main__':
    main()
