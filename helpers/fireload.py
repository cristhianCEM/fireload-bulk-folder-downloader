from helpers.constants import TABLE_ID, DOWNLOAD_LINK_ID, MAX_THREADS
from helpers.filesystem import get_filename_from_url, exists_file
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

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

# Funcion que descarga los archivos de fireload
# el parametro driver es el driver de selenium
def download_fireload_urls(driver, urls, folder_destiny):

    items_in_process = []
    items_to_remove = []
    items_ending = []

    def wait_seconds(seconds=1):
        sleep(seconds)
        for item in items_in_process:
            item['seconds'] += seconds

    def window_open(driver, url):
        driver.execute_script(f"window.open('{url}');")

    def get_download_url(driver):
        try:
            download_link = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, DOWNLOAD_LINK_ID)))
            return download_link.get_attribute('href')
        except:
            print('No se pudo obtener el link de descarga')
            return False

    def exist_file_downloaded(filename):
        return exists_file(folder_destiny, filename)

    while urls or items_in_process:
        # add news item to process
        if len(items_in_process) < MAX_THREADS:
            for _ in range(MAX_THREADS - len(items_in_process)):
                if len(urls) == 0:
                    break
                url = urls.pop()
                items_in_process.append({
                    'url': url,
                    'window_handle': None,
                    'seconds': 0,
                    'filename': get_filename_from_url(url),
                    'download': 'not-started',
                    'success': None
                })
                window_open(driver, url)
                print(f"Se agregó a la cola: {url}")
        # get current active windows
        windows = driver.window_handles[1:]
        # search and map for new windows
        for item in items_in_process:
            if item['window_handle'] is None:
                for window_handle in windows:
                    driver.switch_to.window(window_handle)
                    if driver.current_url == item['url']:
                        item['window_handle'] = window_handle
        # search and map for download button
        for index, item in enumerate(items_in_process):
            if item['window_handle'] is None:
                print("No se encontró la ventana: " + item['url'])
                continue
            if item['download'] == 'not-started':
                driver.switch_to.window(item['window_handle'])
                wait_seconds(1)
                if item['seconds'] < 5:
                    continue
                download_url = get_download_url(driver)
                if download_url == 'javascript:void(0)' or download_url == False:
                    if item['seconds'] > 10:
                        print("No se pudo obtener el link de descarga: " + item['url'])
                        item_deleted = items_in_process.pop(index)
                        item_deleted['success'] = False
                        items_ending.append(item_deleted)
                        driver.close()
                else:
                    print("Iniciando descarga: " + download_url)
                    window_open(driver, download_url)
                    item['download_url'] = download_url
                    item['download'] = 'started'
            else:
                driver.switch_to.window(item['window_handle'])
                wait_seconds(1)
                if exist_file_downloaded(item['filename']):
                    print("Se descargó el archivo: " + item['filename'])
                    item_deleted = items_in_process.pop(index)
                    item_deleted['success'] = True
                    items_ending.append(item_deleted)
                    driver.close()
    string = input("¿Desea cerrar el script? (y/n): ")
    if string == 'y':
        driver.quit()
        print("El navegador se cerró")
    print("El navegador no se cerrará")
