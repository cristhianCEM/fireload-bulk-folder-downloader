import requests
from constants import TABLE_ID, DOWNLOAD_BUTTON_ID, DOWNLOAD_LINK_ID
from multiprocessing import Process, Queue
from selenium.webdriver.edge.service import Service as EdgeService
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
        raise Exception(f'Error: Unable to retrieve page with status code {response.status_code}')
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

def get_download_urls(folder_url):
    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
    fireload_urls = get_fireload_urls(folder_url)
    for url in fireload_urls:
        print("Intentando obtener link de descarga de: " + url)
        driver.get(url)
        # wait for the download button to appear
        WebDriverWait(driver, 10).until(lambda d: d.find_element(By.ID, DOWNLOAD_BUTTON_ID))
        download_button = driver.find_element(By.ID, DOWNLOAD_BUTTON_ID)
        if download_button is None:
            print('No se encontró el botón de descarga')
            continue
        for _ in range(8):
            time.sleep(1)
            download_link = download_button.find_element(By.ID, DOWNLOAD_LINK_ID)
            if download_link is not None:
                break
        if download_link is None:
            print('No se encontró el link de descarga')
            continue
        # get download link
        download_url = download_link.get_attribute('href')
        print(download_url)
    driver.quit()

def descargar_archivo(url, nombre_archivo):
    respuesta = requests.get(url, stream=True)
    tamaño_total = int(respuesta.headers.get('content-length', 0))
    progreso = tqdm(total=tamaño_total, unit='iB', unit_scale=True, desc=nombre_archivo)
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
    # cola = Queue()
    cola = []
    folder_url = "https://www.fireload.com/folder/8a3b80912c40659961540d91060d91d0/501-600"
    get_download_urls(folder_url)
    # proceso_obtener = Process(target=obtener_urls, args=(cola, folder_url))
    # proceso_descargar = Process(target=descargar_archivos, args=(cola,))
    # proceso_obtener.start()
    # proceso_descargar.start()

    # proceso_obtener.join()
    # proceso_descargar.join()