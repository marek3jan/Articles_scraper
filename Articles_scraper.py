import csv
from requests import get
from bs4 import BeautifulSoup
import os
import sys

arguments = list(sys.argv)

def give_me_articles():
    core_html = BeautifulSoup(get(webpage).text, features="html.parser")

    if not core_html.find('div', {'class':  'docsum-content'}):
        return print("Your webpage is wrong".upper())

    else:
        print(f'Downloading data from the chosen webpage: {webpage}')
        pages = (core_html.find('label', {'class': 'of-total-pages'})).text.strip('of ')
        pages = int(pages)
        content = []
        content.append(webpage)

        articles = []
        references = []
        journals = []
        years = []
        doi = []

        for i in range(2, pages+1):
            if pages >= 2:
                page = webpage + f"&page={i}"
                content.append(page)
            else:
                continue

        for i in range(len(content)):
            html = BeautifulSoup(get(content[i]).text, features="html.parser")
            information = html.find_all('div', {'class':  'docsum-content'})
            links = html.find_all('a', {'class': 'docsum-title'})

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
                    idoi = f'https://doi.org/{idoi}'

                doi.append(idoi)

                if info.find('span', {'class': 'docsum-journal-citation short-journal-citation'}):
                    cit = info.find('span', {'class': 'docsum-journal-citation short-journal-citation'}).text
                    year = cit.split('. ')[1].strip('.')
                    journal = cit.split('. ')[0]

                else:
                    year = 'none'
                    journal = 'none'

                years.append(year)
                journals.append(journal)

            for direction in links:
                link = "/".join(content[i].split("/")[:-1]) + "/" + direction['href']
                references.append(link)

                title = direction.text.encode('ascii', 'ignore').decode()
                articles.append(title)

        for i in range(len(articles)):
            dictionary = {}
            articles[i] = articles[i].strip('\n              \n')
            articles[i] = articles[i].strip('\n')
            articles[i] = articles[i].strip('              ')
            dictionary['DOI_WEBPAGE'] = doi[i]
            dictionary['PUBMED_WEBPAGE'] = references[i]
            dictionary['YEAR'] = years[i]
            dictionary['JOURNAL'] = journals[i]
            dictionary['TITLE'] = articles[i]

            mode = "w" if f'{file_name}' not in os.listdir() else "a"
            with open(f'{file_name}', mode, newline='') as file:
                header = list(dictionary.keys())
                row = list(dictionary.values())
                writer = csv.DictWriter(file, fieldnames=header)
                w = csv.writer(file)
                if mode == "w":
                    writer.writeheader()
                w.writerow(row)

        return print('Your csv file has been generated'.upper())



if __name__ == "__main__":
    if len(arguments) < 2:
        print("You forgot to write the first argument to define the name of your csv file.".upper())
    elif len(arguments) > 2:
        print("More arguments than needed.".upper())
    else:
        url = input("Webpage of interest: ".upper())
        arguments.insert(1, url)
        webpage = str(arguments[1])
        file_name = str(arguments[2]) + '.csv'
        give_me_articles()
