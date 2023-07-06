# ==============================================================================
#                                                                              =
#    Copyright (c) 2023. Haixing Hu                                            =
#    All rights reserved.                                                      =
#                                                                              =
# ==============================================================================
import logging
import os
import sys
from typing import List, Dict, Set

from dict_page import DictPage
from zdic_dict_page import ZdicDictPage
from baidu_dict_page import BaiduDictPage

DICT_PAGE_TYPE = 'zdic'
"""
字典页面的类型，可选值为：

- `'zdic'`: 表示使用汉典页面数据
- `'baidu'`: 表示使用百度汉语页面数据
"""


def get_dict_page(ch: str) -> DictPage:
    """
    获取指定汉字的字典页面。

    :param ch: 指定的汉字。
    :return: 指定汉字的字典页面。
    """
    match DICT_PAGE_TYPE:
        case 'zdic':
            return ZdicDictPage(ch)
        case 'baidu':
            return BaiduDictPage(ch)
        case _:
            raise ValueError(f'Unknown dict page type: {DICT_PAGE_TYPE}')


def collect_characters(input_files: List[str]) -> Dict[str, Set[str]]:
    """
    收集所有待制作卡片的汉字及其标签。

    :param input_files: 输入文件的文件名列表。
    :return: 包含所有汉字及其对应的标签的字典。
    """
    logger = logging.getLogger(__name__)
    result = {}
    for input_file in input_files:
        logger.info('Processing input file: %s', input_file)
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
                        logger.info('Reading character %d/%d: %s [%s]', current, total, c, tag)
    return result


def generate_cards(characters: Dict[str, Set[str]], output_file: str):
    """
    生成Anki卡片表格数据并将其写入输出文件。

    :param characters: 包含现有汉字及其对应标签的字典
    :param output_file: 输出文件名。
    """
    logger = logging.getLogger(__name__)
    total = len(characters)
    current = 0
    with open(output_file, 'w', encoding='utf-8') as file:
        for ch, tags in characters.items():
            current += 1
            tags_str = ' '.join(tags)
            logger.info('Processing character %d/%d: %s [%s]', current, total, ch, tags_str)
            page = get_dict_page(ch)
            image = page.get_image()
            pinyin = page.get_pinyin()
            pronounce = page.get_pronounce()
            definitions = page.get_definitions()
            line = f'{tags_str} | {ch} | {pinyin} | {definitions} | {image} | {pronounce}\n'
            file.write(line)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 pinyin_dict.py input_file1 input_file2 ... output_file")
        return
    input_files = sys.argv[1:-1]
    output_file = sys.argv[-1]

    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(name)s - %(message)s")
    if os.path.exists(output_file):
        os.remove(output_file)
    characters = collect_characters(input_files)
    generate_cards(characters, output_file)


if __name__ == '__main__':
    main()
