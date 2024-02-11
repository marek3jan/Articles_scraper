import csv
from requests import get
from bs4 import BeautifulSoup
import os
import sys

arguments = list(sys.argv)

def define_source():
    core_source = BeautifulSoup(get(web_page).text, features="html.parser")

    if core_source.find('div', {'class': 'docsum-content'}):
        source = BeautifulSoup(get(web_page).text, features="html.parser")

    else:
        source = 'none'

    return source

def select_pages():
    source = define_source()
    if source != 'none':
        pages = int((source.find('label', {'class': 'of-total-pages'})).text.strip('of '))

    else:
        pages = 'none'

    return pages

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

    else:
        content_archive = 'none'

    return content_archive

def create_list_of_information():
    content = create_content_archive()

    if content != 'none':
        list_of_information: list = []

        webdoi = []
        doi = []
        years = []
        journals = []
        articles = []

        for i in range(len(content)):
            html = BeautifulSoup(get(content[i]).text, features="html.parser")
            information = html.find_all('div', {'class': 'docsum-content'})
            links = html.find_all('a', {'class': 'docsum-title'})

            for direction in links:
                title = direction.text.encode('ascii', 'ignore').decode()
                title = title.strip('\n              \n')
                title = title.strip('\n')
                title = title.strip('              ')
                articles.append(title)

            for info in information:
                if not info.find('span', {'class': 'docsum-journal-citation full-journal-citation'}):
                    idoi = 'none'

                elif not info.find('span', {'class': 'docsum-journal-citation full-journal-citation'}).text.split('doi: '):
                    idoi = 'none'

                else:
                    idoi = info.find('span', {'class': 'docsum-journal-citation full-journal-citation'}).text.split('doi: ')
                    idoi = idoi[-1].split('. ')

                    if idoi[0][-1] == '.':
                        idoi = idoi[0][0:-1]
                    else:
                        idoi = idoi[0]

                    linkdoi = f'https://doi.org/{idoi}'

                doi.append(idoi)
                webdoi.append(linkdoi)

                if info.find('span', {'class': 'docsum-journal-citation short-journal-citation'}):
                    cit = info.find('span', {'class': 'docsum-journal-citation short-journal-citation'}).text
                    year = cit.split('. ')[1].strip('.')
                    journal = cit.split('. ')[0]

                else:
                    year = 'none'
                    journal = 'none'

                years.append(year)
                journals.append(journal)

        list_of_information.append(webdoi)
        list_of_information.append(doi)
        list_of_information.append(years)
        list_of_information.append(journals)
        list_of_information.append(articles)

    else:
        list_of_information = 'none'

    return list_of_information


def create_dictionary_and_write_to_csv():
    my_list = create_list_of_information()

    if my_list == 'none':
        Termination = True
        return Termination

    else:
        for i in range(len(my_list[4])):
            dictionary: dict = {}
            dictionary['Web Source'] = my_list[0][i]
            dictionary['DOI'] = my_list[1][i]
            dictionary['Year'] = my_list[2][i]
            dictionary['Scientific Journal'] = my_list[3][i]
            dictionary['Article Title'] = my_list[4][i]

            mode = "w" if f'{file_name}' not in os.listdir() else "a"
            with open(f'{file_name}', mode, newline='') as file:
                header = list(dictionary.keys())
                row = list(dictionary.values())
                writer = csv.DictWriter(file, fieldnames=header)
                w = csv.writer(file)
                if mode == "w":
                    writer.writeheader()
                w.writerow(row)


if __name__ == "__main__":
    if len(arguments) < 2:
        print("You forgot to write the first argument to define the name of your csv file.".upper())
    elif len(arguments) > 2:
        print("More arguments than needed.".upper())
    else:
        url = input("Webpage of interest: ".upper())
        arguments.insert(1, url)
        web_page = str(arguments[1])
        file_name = str(arguments[2]) + '.csv'

        create_dictionary_and_write_to_csv()

        print("Your csv file should be ready, otherwise you selected wrong website".upper())
