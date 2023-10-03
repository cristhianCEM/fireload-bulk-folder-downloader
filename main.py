import requests
from os import path
from constants import TABLE_ID, DOWNLOAD_BUTTON_ID, DOWNLOAD_LINK_ID
from multiprocessing import Process, Queue
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

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

def download_urls(driver, folder_url, threads=5):
    urls = get_fireload_urls(folder_url)[:10]
    items_in_process = []
    items_errors = []
    items_success = []
    def get_index_by_url(url):
        for index, item in enumerate(items_in_process):
            if item['url'] == url:
                return index
        return None

    def wait_seconds(seconds=1):
        time.sleep(seconds)
        for item in items_in_process:
            item['seconds'] += seconds

    def window_open(driver, url):
        driver.execute_script(f"window.open('{url}');")

    while (True):
        len_items_in_process = len(items_in_process)
        if len(urls) == 0 and len_items_in_process == 0:
            break
        if len_items_in_process < threads:
            for _ in range(threads - len_items_in_process):
                if len(urls) == 0:
                    break
                url = urls.pop()
                items_in_process.append({
                    'url': url,
                    'seconds': 0
                })
                window_open(driver, url)
                print("se agrego a la cola: " + url)
        for window_handle in driver.window_handles[1:]:
            driver.switch_to.window(window_handle)
            current_url = driver.current_url
            index = get_index_by_url(current_url)
            if index is None:
                driver.close()
                continue
            item = items_in_process[index]
            if item['seconds'] < 5:
                wait_seconds(1)
                continue
            download_button = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, DOWNLOAD_BUTTON_ID)))
            if download_button is None:
                print('No se encontró el botón de descarga')
                continue
            download_link = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, DOWNLOAD_LINK_ID)))
            if download_link is None:
                print('No se encontró el link de descarga')
                continue
            download_url = download_link.get_attribute('href')
            current_item = {
                'url': current_url,
                'download_url': download_url
            }
            if download_url == 'javascript:void(0)':
                if item['seconds'] > 10:
                    items_errors.append(current_item)
                    items_in_process.pop(index)
                    print("No se pudo obtener el link de descarga: " + current_url)
                    driver.close()
            else:
                print("Link de descarga obtenido: " + download_url)
                items_success.append(current_item)
                items_in_process.pop(index)
                window_open(driver, download_url)
            wait_seconds(1)
    string = input("¿Desea cerrar el script? (y/n): ")
    if string == 'y':
        driver.quit()
        print("El navegador se cerró")
    print("El navegador no se cerrará")

def descargar_archivo(url, nombre_archivo):
    respuesta = requests.get(url, stream=True)
    tamaño_total = int(respuesta.headers.get('content-length', 0))
    progreso = tqdm(total=tamaño_total, unit='iB',
                    unit_scale=True, desc=nombre_archivo)
    with open(nombre_archivo, 'wb') as archivo:
        for chunk in respuesta.iter_content(chunk_size=8192):
            progreso.update(len(chunk))
            archivo.write(chunk)
    progreso.close()

def descargar_archivos(cola):
    while not cola.empty():
        url = cola.get()
        nombre_archivo = url.split("/")[-1]
        descargar_archivo(url, nombre_archivo)

if __name__ == "__main__":
    cola = []
    folder_url = "https://www.fireload.com/folder/8a3b80912c40659961540d91060d91d0/501-600"
    folder_destiny = path.abspath(".\downloads")
    options = webdriver.EdgeOptions()
    options.add_argument('log-level=3')
    options.add_experimental_option("prefs", {
        "download.default_directory": folder_destiny,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    # options.add_argument('--headless')
    service = EdgeService(EdgeChromiumDriverManager().install())
    # service.log_path = "NUL"
    # service.command_line_args().append("--log-level=3")
    driver = webdriver.Edge(service=service, options=options)
    download_urls(driver, folder_url)
    # proceso_obtener = Process(target=obtener_urls, args=(cola, folder_url))
    # proceso_descargar = Process(target=descargar_archivos, args=(cola,))
    # proceso_obtener.start()
    # proceso_descargar.start()

    # proceso_obtener.join()
    # proceso_descargar.join()