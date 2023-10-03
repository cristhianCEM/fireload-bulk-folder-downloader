from helpers.filesystem import create_destiny_folder
from helpers.fireload import get_fireload_urls, download_fireload_urls
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium import webdriver

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