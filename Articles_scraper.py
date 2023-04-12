import csv
from requests import get
from bs4 import BeautifulSoup
import os
import sys

arguments = list(sys.argv)

def write_csv_file():
    core_html = BeautifulSoup(get(webpage).text, features="html.parser")

    if not core_html.find('div', {'class':  'docsum-content'}):
        return print("Your webpage is wrong".upper())

    else:
        print(f'Downloading data from the chosen webpage: {webpage}')
        pages = (core_html.find('label', {'class': 'of-total-pages'})).text.strip('of ')
        pages = int(pages)
        zoznam = []
        zoznam.append(webpage)

        clanky = []
        odkazy = []
        journals = []
        years = []
        doi = []

        for i in range(2, pages+1):
            if pages >= 2:
                page = webpage + f"&page={i}"
                zoznam.append(page)
            else:
                continue

        for i in range(len(zoznam)):
            html = BeautifulSoup(get(zoznam[i]).text, features="html.parser")
            informacie = html.find_all('div', {'class':  'docsum-content'})
            linky = html.find_all('a', {'class': 'docsum-title'})

            for info in informacie:
                idoi = info.find('span', {'class': 'docsum-journal-citation full-journal-citation'}).text.split('doi: ')
                idoi = idoi[-1].split('. ')

                if idoi[0][-1] == '.':
                    idoi = idoi[0][0:-1]
                else:
                    idoi = idoi[0]
                idoi = f'https://doi.org/{idoi}'

                doi.append(idoi)
                cit = info.find('span', {'class': 'docsum-journal-citation short-journal-citation'}).text
                year = cit.split('. ')[1].strip('.')
                years.append(year)
                journal = cit.split('. ')[0]
                journals.append(journal)

            for clen in linky:
                link = "/".join(zoznam[i].split("/")[:-1]) + "/" + clen['href']
                odkazy.append(link)

                nadpis = clen.text
                clanky.append(nadpis)

        for i in range(len(clanky)):
            slovnik = {}
            clanky[i] = clanky[i].strip('\n              \n')
            clanky[i] = clanky[i].strip('\n')
            clanky[i] = clanky[i].strip('              ')
            slovnik['DOI_WEBPAGE'] = doi[i]
            slovnik['PUBMED_WEBPAGE'] = odkazy[i]
            slovnik['YEAR'] = years[i]
            slovnik['JOURNAL'] = journals[i]
            slovnik['TITLE'] = clanky[i]

            mode = "w" if f'{file_name}' not in os.listdir() else "a"
            with open(f'{file_name}', mode, newline='') as file:
                header = list(slovnik.keys())
                row = list(slovnik.values())
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
        url = input("Insert your webpage: ".upper())
        arguments.insert(1, url)
        webpage = str(arguments[1])
        file_name = str(arguments[2]) + '.csv'
        write_csv_file()
