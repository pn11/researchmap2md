import argparse
from logging import getLogger, StreamHandler, DEBUG
from typing import Literal

import polars as pl

logger = getLogger(__name__)

CsvType = Literal['presentations', 'published_papers']

class NotSupportedError(Exception):
    pass


def main():
    args = parse_args()
    md = researchmap2csv(args.input_file)

    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(md)
    else:
        print(md)


def parse_args(args=None):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('input_file')
    parser.add_argument('-o', '--output_file')

    if args is None:
        return parser.parse_args()
    else:
        return parser.parse_args(args)


def researchmap2csv(filename: str) -> str:
    csv_type = get_csv_type(filename)
    df = pl.read_csv(filename, skip_rows=1)

    if csv_type == 'presentations':
        md = build_presentation(df)
    elif csv_type == 'published_papers':
        md = build_paper(df)
    return md


def build_paper(df: pl.DataFrame) -> str:
    paper_style = {
        'scientific_journal': '研究論文（学術雑誌）',
        'international_conference_proceedings': '研究論文（国際会議プロシーディングス）',
        'research_institution': '研究論文（大学，研究機関等紀要）',
        'symposium': '研究論文（研究会，シンポジウム資料等）',
        'research_society': '研究論文（その他学術会議資料等）',
        'in_book': '論文集(書籍)内論文',
        'master_thesis': '学位論文（修士）',
        'doctoral_thesis': '学位論文（博士）'
    }

    out_str = "\n## 論文\n"

    # 投稿論文の場合
    out_str += "\n### 投稿論文\n\n"
    for i, row_dict in enumerate(df.to_dicts()):
        if row_dict['掲載種別'] != 'scientific_journal':
            break
        out_str += f"""1. {row_dict['著者(英語)']}, {row_dict['タイトル(英語)']}, *{row_dict['誌名(英語)']}*, {row_dict['巻']}, {row_dict['号']}, pp{row_dict['開始ページ']}-{row_dict['終了ページ']} ({row_dict['出版年月']}).  {display_urls(row_dict)}
"""

    # プロシーディングスの場合
    out_str += "\n### プロシーディングス\n\n"
    for i, row_dict in enumerate(df.to_dicts()):
        if row_dict['掲載種別'] != 'international_conference_proceedings':
            break
        out_str += f"""1. {row_dict['著者(英語)']}, {row_dict['タイトル(英語)']}, *{row_dict['誌名(英語)']}*, {row_dict['巻']}, {row_dict['号']}, pp{row_dict['開始ページ']}-{row_dict['終了ページ']} ({row_dict['出版年月']}).  {display_urls(row_dict)}
"""

    return out_str


def build_presentation(df: pl.DataFrame) -> str:
    presentation_style = {
        'poster_presentation': 'ポスター発表',
        'oral_presentation': '口頭発表'
    }

    out_str = "\n## 発表\n"

    # 国際会議の場合
    out_str += "\n### 国際会議\n\n"
    for row_dict in df.to_dicts():
        if row_dict['国際・国内会議'] == True:
            out_str += f"""1. {row_dict['会議名(英語)']}, {presentation_style[row_dict['会議種別']]}, "{row_dict['タイトル(英語)']}", {row_dict['開催地(英語)']}, {row_dict['国・地域']}.  
  {row_dict['講演者(英語)']}  {display_urls(row_dict)}
"""
            
    # 国内会議の場合
    out_str += "\n### 国内会議\n\n"
    for row_dict in df.to_dicts():
        if row_dict['国際・国内会議'] == False:
            out_str += f"""1. {row_dict['会議名(日本語)']}, {presentation_style[row_dict['会議種別']]}, "{row_dict['タイトル(日本語)']}", {row_dict['開催地(日本語)']}, {row_dict['国・地域']}.  
  {row_dict['講演者(日本語)']}  {display_urls(row_dict)}
"""

    return out_str


def display_urls(row_dict: dict, num_indent: int = 4):
    '''
    >>> display_urls({"URL": "https://example.com", "URL2": "https://example.com"})
    '\\n    - <https://example.com>\\n    - <https://example.com>'
    >>> display_urls({"URL": "null", "URL2": "https://example.com"})
    '\\n    - <https://example.com>'
    >>> display_urls({"URL": "https://example.com", "URL2": "null"})
    '\\n    - <https://example.com>'
    >>> display_urls({"URL": "null", "URL2": "null"})
    ''
    '''
    urls = []
    if row_dict['URL'] != 'null':
        urls.append(row_dict['URL'])
    if row_dict['URL2'] != 'null':
        urls.append(row_dict['URL2'])

    urls = [f"{' '*num_indent}- <{url}>" for url in urls]

    if len(urls) > 0:
        return '\n' + '\n'.join(urls)
    else:
        return ''


def get_csv_type(filename: str) -> CsvType:
    with open(filename, encoding='utf-8-sig') as f:
        line = f.readline().strip()

    if line == 'presentations':
        return line
    elif line == 'published_papers':
        return line
    else:
        print(line == 'presentations')
        logger.error("presentations と published_papers にのみ対応しています。")
        raise NotSupportedError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    main()
