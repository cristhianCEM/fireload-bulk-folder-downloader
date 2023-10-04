import os
from time import sleep
from helpers.filesystem import create_destiny_folder
from helpers.fireload import get_fireload_urls, download_fireload_urls
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium import webdriver

if __name__ == "__main__":
    path_extension = os.path.abspath("./crx/addblock-5.10.1-edge")
    folder_url = "https://www.fireload.com/folder/8a3b80912c40659961540d91060d91d0/501-600"
    folder_destiny = create_destiny_folder(folder_url)
    print("Carpeta de destino: " + folder_destiny)
    options = webdriver.EdgeOptions()
    options.add_argument('log-level=3')
    options.add_argument('load-extension=' + path_extension)
    options.add_experimental_option("prefs", {
        "download.default_directory": folder_destiny,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    # options.add_argument('--headless')
    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)
    # wait 20 seconds for install extension
    urls = get_fireload_urls(folder_url)
    print("Cantidad de archivos a descargar: " + str(len(urls)))
    print("Instalando extensión...espere 20 segundos")
    sleep(20)
    download_fireload_urls(driver, urls[::-1], folder_destiny)