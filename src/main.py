import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEPS_DOC_URL
from exceptions import ParserFindTextException
from outputs import control_output
from utils import find_tag, get_soup


def whats_new(session):
    """Парсинг новвоведений в python"""

    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    soup = get_soup(session, whats_new_url)

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'})

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])

        soup = get_soup(session, version_link)

        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session):
    """Парсинг ссылок c документацией на различные версии python"""

    soup = get_soup(session, MAIN_DOC_URL)

    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindTextException('Не найден список c версиями Python')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )

    return results


def download(session):
    """Загрузка архива с файлами документации в формете HTML"""

    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')

    soup = get_soup(session, downloads_url)

    main_tag = find_tag(soup, 'div', attrs={'role': 'main'})

    table_tag = find_tag(main_tag, 'table', attrs={'class': 'docutils'})

    html_doc_tag = find_tag(table_tag, 'a', attrs={
                            'href': re.compile(r'.+html\.zip$')})

    html_doc_link = html_doc_tag['href']
    archive_url = urljoin(downloads_url, html_doc_link)

    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    """Парсинг PEP"""

    soup = get_soup(session, PEPS_DOC_URL)

    sections = find_tag(soup, 'section', attrs={'id': 'index-by-category'})
    tbodies = sections.find_all('tbody')

    status_summary = {}
    total = 0
    msg_log = []
    for tbody in tqdm(tbodies):
        tr_tags = tbody.find_all('tr')
        for tr_tag in tr_tags:
            status = tr_tag.find('abbr').text[1:]
            total += 1
            status_pep_page = tr_tag.find('a')['href']
            url_pep_page = urljoin(PEPS_DOC_URL, status_pep_page)
            soup = get_soup(session, url_pep_page)

            status_tag = find_tag(soup, 'dl')
            block_match = re.search(
                r'<dt[^>]*>\s*Status\s*.*?</dt>\s*<dd[^>]*>(.*?)</dd>',
                str(status_tag)
            )

            status_in_page = 'Unknown'
            if block_match:
                dd_content = block_match.group(1)
                text_match = re.search(r'>([^<]+)<', dd_content)
                if text_match:
                    status_in_page = text_match.group(1).strip()

            if status_in_page not in EXPECTED_STATUS.get(status, ()):
                msg_log.append(
                    f'Неожиданный статус PEP {url_pep_page}: {status_in_page}'
                )

            status_summary[status_in_page] = status_summary.get(
                status_in_page, 0) + 1
    for msg in msg_log:
        logging.warning(msg)

    results = [('Статус', 'Количество')]
    results.extend(tuple(status_summary.items()))
    results.append(('Total', total))

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode

    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
