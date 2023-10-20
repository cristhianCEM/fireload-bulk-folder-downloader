import os
from time import sleep
from helpers.filesystem import create_destiny_folder
from helpers.fireload import get_fireload_table_from_file, download_fireload_table
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium import webdriver

if __name__ == "__main__":
    path_extension = os.path.abspath("./crx/addblock-5.10.1-edge")
    folder_destiny = create_destiny_folder("op")
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
    fireload_table = get_fireload_table_from_file("downloads/list.txt")
    print("Cantidad de archivos a descargar: " + str(len(fireload_table)))
    print("Instalando extensión... espere 15 segundos")
    sleep(15)
    download_fireload_table(driver, fireload_table[::-1], folder_destiny)