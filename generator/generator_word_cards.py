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


def collect_words(input_files: List[str]) -> Dict[str, Set[str]]:
    """
    收集所有待制作卡片的生词及其标签。

    :param input_files: 输入文件的文件名列表。
    :return: 包含所有生词及其对应的标签的字典。
    """
    logger = logging.getLogger(__name__)
    result = {}
    for input_file in input_files:
        logger.info('Processing input file: %s', input_file)
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            book = os.path.splitext(os.path.basename(input_file))[0]
            chapter = ''
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    chapter = line[1:].strip()
                elif line:
                    tag = f'{book}{chapter}'
                    chars = [c.strip() for c in line.split('、') if c.strip()]
                    total = len(chars)
                    current = 0
                    for c in chars:
                        current += 1
                        if c in result:
                            result[c].add(tag)
                        else:
                            result[c] = {tag}
                        logger.info('Reading word %d/%d: %s [%s]', current, total, c, tag)
    return result


def generate_cards(words: Dict[str, Set[str]], output_file: str):
    """
    生成Anki卡片表格数据并将其写入输出文件。

    :param words: 包含现有生词及其对应标签的字典
    :param output_file: 输出文件名。
    """
    logger = logging.getLogger(__name__)
    total = len(words)
    current = 0
    with open(output_file, 'w', encoding='utf-8') as file:
        for word, tags in words.items():
            current += 1
            tags_str = ' '.join(tags)
            logger.info('Processing word %d/%d: %s [%s]', current, total, word, tags_str)
            line = f'{word}|{tags_str}\n'
            file.write(line)


def main():
    if len(sys.argv) < 3:
        print(f'Usage: python3 {sys.argv[0]} input_file1 input_file2 ... output_file')
        return
    input_files = sys.argv[1:-1]
    output_file = sys.argv[-1]

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s - %(message)s')
    if os.path.exists(output_file):
        os.remove(output_file)
    words = collect_words(input_files)
    generate_cards(words, output_file)


if __name__ == '__main__':
    main()
