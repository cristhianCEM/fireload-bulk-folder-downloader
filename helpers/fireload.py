from helpers.constants import TABLE_ID, DOWNLOAD_LINK_ID, DOWNLOAD_BUTTON_ID, MAX_THREADS
from helpers.filesystem import get_filename_from_url, exists_file
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


def get_fireload_table_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    rows = []
    for line in lines:
        if line.startswith('https://www.fireload.com/'):
            url = line.strip()
            rows.append({
                'url': url,
                'filename': get_filename_from_url(url)
            })
    return rows

# Funcion que obtiene los links de descarga de fireload
# el parametro folder_url es la url de la carpeta de fireload


def get_fireload_table_data(folder_url):
    response = requests.get(folder_url)
    if response.status_code != 200:
        raise Exception(
            f'Error: Unable to retrieve page with status code {response.status_code}')
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find(id=TABLE_ID)
    if table is None:
        raise Exception('Error: Unable to find table with id ' + TABLE_ID)
    rows = table.find_all('tr')
    table_data = []
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
        filename = link.text
        table_data.append({
            'url': url,
            'filename': filename
        })
    return table_data

# Funcion que descarga los archivos de fireload
# el parametro driver es el driver de selenium


def download_fireload_table(driver, table_data, folder_destiny):

    items_in_process = []
    items_to_remove = []
    items_ending = []

    def wait_seconds(seconds=1):
        sleep(seconds)
        for item in items_in_process:
            item['seconds'] += seconds

    def window_open(driver, url):
        driver.execute_script(f"window.open('{url}');")

    def click_valid_download_link(driver, show_error=False):
        try:
            download_button = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, DOWNLOAD_BUTTON_ID)))
            download_link = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, DOWNLOAD_LINK_ID)))
            href_value = download_link.get_attribute('href')
            if href_value and href_value != 'javascript:void(0)':
                download_button.click()
                print(f"Iniciando descarga: {href_value}")
                return href_value
            else:
                if show_error:
                    print('El enlace de descarga no es válido')
                return False
        except:
            if show_error:
                print('No se pudo hacer click en el link de descarga')
            return False

    def exist_file_downloaded(filename):
        return exists_file(folder_destiny, filename)

    def add_item_to_remove(index, success=True):
        items_to_remove.append(index)
        items_in_process[index]['success'] = success

    default_window = driver.current_window_handle
    tabs_windows = []
    while table_data or items_in_process:
        # add news item to process
        if len(items_in_process) < MAX_THREADS:
            driver.switch_to.window(default_window)
            for _ in range(MAX_THREADS - len(items_in_process)):
                if len(table_data) == 0:
                    break
                table_item = table_data.pop()
                url = table_item['url']
                filename = table_item['filename']
                items_in_process.append({
                    'url': url,
                    'window_handle': None,
                    'seconds': 0,
                    'filename': filename,
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
                    sleep(0.5)
                    if driver.current_url == item['url']:
                        item['window_handle'] = window_handle
                        tabs_windows.append(window_handle)
        # search and map for download button
        for index, item in enumerate(items_in_process):
            if item['window_handle'] is None:
                print("No se encontró la ventana: " + item['url'])
                continue
            driver.switch_to.window(item['window_handle'])
            wait_seconds(1)
            if item['download'] == 'not-started':
                if item['seconds'] < 5:
                    continue
                if exist_file_downloaded(item['filename']):
                    print("El archivo ya existe: " + item['filename'])
                    add_item_to_remove(index, True)
                    continue
                download_url = click_valid_download_link(driver, True)
                if download_url == False:
                    if item['seconds'] > 10:
                        print("No se pudo obtener el link de descarga: " + item['url'])
                        add_item_to_remove(index, False)
                else:
                    items_in_process[index]['download'] = 'started'
            else:
                if exist_file_downloaded(item['filename']):
                    print(f"Se descargó el archivo: {item['filename']}")
                    add_item_to_remove(index, True)
                else:
                    click_valid_download_link(driver)
                    print('.', end='', flush=True)
        # remove items already downloaded
        for index in reversed(items_to_remove):
            item_deleted = items_in_process.pop(index)
            items_ending.append(item_deleted)
            tabs_windows.remove(item_deleted['window_handle'])
        items_to_remove.clear()
        # close tabs windows that no is in process
        for window_index in windows:
            if window_index not in tabs_windows:
                try:
                    driver.switch_to.window(window_index)
                    sleep(1)
                    driver.close()
                except Exception as e:
                    print(f"Se intentó cerrar una ventana pero no se pudo({window_index})")
                    pass
    string = input("¿Desea cerrar el script? (y/n): ")
    if string == 'y':
        driver.quit()
        print("El navegador se cerró")
    else:
        print("El navegador no se cerrará")
