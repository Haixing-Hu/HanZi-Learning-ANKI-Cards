import os
import sys
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from typing import List, Dict, Set


def get_page_content(character: str) -> bytes:
  """
  获取汉字对应的汉典网页面内容

  :param chinese: 汉字
  :return: 汉字对应的汉典网页面内容
  """
  url = f"http://www.zdic.net/hans/{quote(character)}"
  response = requests.get(url)
  return response.content


def get_pinyin(soup: BeautifulSoup) -> str:
  """
  从汉典网页面中抽取汉字的拼音

  :param soup: 解析后的汉典网页面对象
  :return: 汉字的拼音
  """
  pinyin_element = soup.select_one('span.dicpy')
  if pinyin_element:
    pinyin_text = pinyin_element.contents[0].strip().split()[0]
    return pinyin_text
  return ''


def get_definitions(soup: BeautifulSoup, character: str) -> str:
  """
  从汉典网页面中抽取汉字的解释

  :param soup: 解析后的汉典网页面对象
  :param chinese: 汉字
  :return: 汉字的解释
  """
  definitions_element = soup.select_one('.content.definitions.jnr > ol')
  if definitions_element:
    definitions = []
    for index, li in enumerate(definitions_element.find_all('li'), 1):
      definition = li.text.strip().replace('～', character)
      definitions.append(f"{index}. {definition}")
    return '<br>'.join(definitions)
  return ''


def collect_existing_characters(input_files: List[str]) -> Dict[str, Set[str]]:
  """
  收集现有的汉字、拼音和标签

  :param input_files: 输入文件列表
  :return: 包含现有汉字及其对应拼音、解释和标签的字典
  """
  existing_characters = {}

  for input_file in input_files:
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
          characters = [c.strip() for c in line.split('、') if c.strip()]
          total = len(characters)
          current = 0
          for c in characters:
            current += 1
            if c in existing_characters:
              existing_characters[c].add(tag)
            else:
              existing_characters[c] = set([tag])
            progress = current / total * 100
            print(f'Reading character {current}/{total} - Progress: {progress:.2f}% : {c} [{tag}]')
  return existing_characters


def generate_cards(existing_characters: Dict[str, Set[str]], output_file: str):
  """
  生成Anki卡片并将其写入输出文件

  :param existing_characters: 包含现有汉字及其对应标签的字典
  :param output_file: 输出文件名
  """
  total = len(existing_characters)
  current = 0
  with open(output_file, 'w', encoding='utf-8') as file:
    for character, tags in existing_characters.items():
      current += 1
      content = get_page_content(character)
      soup = BeautifulSoup(content, 'html.parser')
      pinyin = get_pinyin(soup)
      definitions = get_definitions(soup, character)
      tags_str = ' '.join(tags)
      line = f'{tags_str} | {character} | {pinyin} | {definitions}\n'
      file.write(line)
      progress = current / total * 100
      print(f'Processing character {current}/{total} - Progress: {progress:.2f}% : {character} [{tags_str}]')


def main():
  if len(sys.argv) < 3:
    print("Usage: python3 pinyin_dict.py input_file1 input_file2 ... output_file")
    return

  input_files = sys.argv[1:-1]
  output_file = sys.argv[-1]

  # 删除已存在的输出文件
  if os.path.exists(output_file):
    os.remove(output_file)

  existing_words = collect_existing_characters(input_files)
  generate_cards(existing_words, output_file)


if __name__ == '__main__':
  main()
