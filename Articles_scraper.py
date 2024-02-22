import csv
from requests import get
from bs4 import BeautifulSoup
import os
import sys

arguments = list(sys.argv)


def define_source():
    core_source = BeautifulSoup(get(web_page).text, features="html.parser")

    if core_source.find('div', {'class': 'docsum-content'}):
        print(f"Your csv_file is now being generated from the source {arguments[2]}")
        return BeautifulSoup(get(web_page).text, features="html.parser")

    else:
        print('Your selected website is not compatible with this web-scraper.')
        return 'none'


def select_pages():
    source = define_source()
    if source != 'none':
        return int((source.find('label', {'class': 'of-total-pages'})).text.strip('of '))

    else:
        return 'none'


def create_content_archive():
    content_archive: list = []
    pages = select_pages()
    if pages != 'none':
        content_archive.append(web_page)

        for i in range(2, pages + 1):
            if pages < 2:
                continue
            else:
                page = web_page + f"&page={i}"
                content_archive.append(page)
        return content_archive

    else:
        return 'none'


def return_title(a):
    title = a.text.encode('ascii', 'ignore').decode()
    title = title.strip('\n              \n')
    title = title.strip('\n')
    title = title.strip('              ')

    return title


def return_doi(b):
    if not b.find('span', {'class': 'docsum-journal-citation full-journal-citation'}):
        idoi = 'none'

    elif not b.find('span', {'class': 'docsum-journal-citation full-journal-citation'}).text.split(
            'doi: '):
        idoi = 'none'

    else:
        idoi = b.find('span', {'class': 'docsum-journal-citation full-journal-citation'}).text.split(
            'doi: ')
        idoi = idoi[-1].split('. ')
        if len(idoi) == 0:
            idoi = 'none'
        elif idoi[-1] == '.':
            idoi = idoi[0:-1]
        else:
            idoi = idoi

    return idoi


def return_url(c):
    base_url = 'https://doi.org'
    link = base_url + c
    return link


def return_year_journal(d):
    if d.find('span', {'class': 'docsum-journal-citation short-journal-citation'}):
        cit = d.find('span', {'class': 'docsum-journal-citation short-journal-citation'}).text
        year = cit.split('. ')[1].strip('.')
        journal = cit.split('. ')[0]

    else:
        year = 'none'
        journal = 'none'

    return year, journal


def return_information():
    content = create_content_archive()
    webdoi = []
    doi = []
    years = []
    journals = []
    articles = []

    if content != 'none':

        for i in range(len(content)):
            html = BeautifulSoup(get(content[i]).text, features="html.parser")
            information = html.find_all('div', {'class': 'docsum-content'})
            links = html.find_all('a', {'class': 'docsum-title'})

            for info in information:
                idoi = return_doi(info)
                doi.append(idoi)
                webdoi.append(return_url(idoi))
                year, journal = return_year_journal(info)
                years.append(year)
                journals.append(journal)

            for direction in links:
                title = return_title(direction)
                articles.append(title)

    return doi, webdoi, years, journals, articles


def create_dictionary_and_write_to_csv():
    doi, webdoi, years, journals, articles = return_information()

    if len(articles) == 0:
        termination = True
        return termination

    else:
        for i in range(len(articles)):
            dictionary = dict()
            dictionary['Web Source'] = webdoi[i]
            dictionary['DOI'] = doi[i]
            dictionary['Year'] = years[i]
            dictionary['Scientific Journal'] = journals[i]
            dictionary['Article Title'] = articles[i]

            mode = "w" if f'{file_name}' not in os.listdir() else "a"
            with open(f'{file_name}', mode, newline='') as file:
                header = list(dictionary.keys())
                row = list(dictionary.values())
                writer = csv.DictWriter(file, fieldnames=header)
                w = csv.writer(file)
                if mode == "w":
                    writer.writeheader()
                w.writerow(row)
        print('Your csv file has been generated'.upper())


if __name__ == "__main__":
    if len(list(sys.argv)) < 3:
        print("Not enough arguments.".upper())
    elif len(list(sys.argv)) > 3:
        print("More arguments than needed.".upper())
    else:
        file_name = arguments[1] + '.csv'
        web_page = arguments[2]
        create_dictionary_and_write_to_csv()
