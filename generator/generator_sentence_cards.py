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

logger = logging.getLogger(__name__)


def add_sentence(sentence: str, book: str, chapter: str, result: Dict[str, Set[str]]):
    if sentence:
        tag = f'{book}{chapter}'
        if sentence in result:
            result[sentence].add(tag)
        else:
            result[sentence] = {tag}
        logger.info('Reading sentence: %s [%s]', sentence, tag)


def collect_sentences(input_files: List[str]) -> Dict[str, Set[str]]:
    """
    收集所有待制作卡片的句子及其标签。

    :param input_files: 输入文件的文件名列表。
    :return: 包含所有句子及其对应的标签的字典。
    """
    result = {}
    for input_file in input_files:
        logger.info('Processing input file: %s', input_file)
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            book = os.path.splitext(os.path.basename(input_file))[0]
            chapter = ''
            sentence = ''
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    add_sentence(sentence, book, chapter, result)
                    sentence = ''
                    chapter = line[1:].strip()
                elif line:
                    # if sentence:
                    #     sentence += '<br>'
                    sentence += line
                else:
                    add_sentence(sentence, book, chapter, result)
                    sentence = ''
            add_sentence(sentence, book, chapter, result)
    return result


def generate_cards(sentences: Dict[str, Set[str]], output_file: str):
    """
    生成Anki卡片表格数据并将其写入输出文件。

    :param sentences: 包含现有句子及其对应标签的字典
    :param output_file: 输出文件名。
    """
    logger = logging.getLogger(__name__)
    total = len(sentences)
    current = 0
    with open(output_file, 'w', encoding='utf-8') as file:
        for sentence, tags in sentences.items():
            current += 1
            tags_str = ' '.join(tags)
            logger.info('Processing sentence %d/%d: %s [%s]', current, total, sentence, tags_str)
            line = f'{sentence}|{tags_str}\n'
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
    sentences = collect_sentences(input_files)
    generate_cards(sentences, output_file)


if __name__ == '__main__':
    main()
