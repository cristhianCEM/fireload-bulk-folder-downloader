from bs4 import BeautifulSoup
import requests
from helpers.constants import TABLE_ID

# Funcion que obtiene los links de descarga de fireload
# el parametro folder_url es la url de la carpeta de fireload
def get_fireload_urls(folder_url):
    response = requests.get(folder_url)
    if response.status_code != 200:
        raise Exception(
            f'Error: Unable to retrieve page with status code {response.status_code}')
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find(id=TABLE_ID)
    if table is None:
        raise Exception('Error: Unable to find table with id ' + TABLE_ID)
    rows = table.find_all('tr')
    urls = []
    for row in rows:
        columns = row.find_all('td')
        if len(columns) == 0:
            continue
        key_column = columns[1]
        link = key_column.find('a')
        if link is None:
            print('Not found page link')
            continue
        url = link['href']
        urls.append(url)
    return urls