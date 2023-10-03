from helpers.constants import DOWNLOAD_BUTTON_ID, DOWNLOAD_LINK_ID, MAX_THREADS
from helpers.filesystem import get_filename_from_url, create_destiny_folder
from helpers.fireload import get_fireload_urls
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

def download_fireload_urls(driver, urls, folder_destiny):
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
        if len_items_in_process < MAX_THREADS:
            for _ in range(MAX_THREADS - len_items_in_process):
                if len(urls) == 0:
                    break
                url = urls.pop()
                items_in_process.append({
                    'url': url,
                    'seconds': 0,
                    'filename': get_filename_from_url(url)
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

if __name__ == "__main__":
    folder_url = "https://www.fireload.com/folder/8a3b80912c40659961540d91060d91d0/501-600"
    folder_destiny = create_destiny_folder(folder_url)
    print("Carpeta de destino: " + folder_destiny)
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
    driver = webdriver.Edge(service=service, options=options)
    urls = get_fireload_urls(folder_url)
    download_fireload_urls(driver, urls, folder_destiny)