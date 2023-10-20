from re import sub as re_sub
from random import choices as random_choices
from urllib.parse import urlparse
from string import ascii_letters, digits
import os

# Función para obtener y formatear el nombre de la carpeta de la URL
# o generar uno aleatorio si es invalido o Nulo
def get_folder_from_url(folder_url):
    parsed_url = urlparse(folder_url)
    path_parts = parsed_url.path.strip("/").split("/")
    folder_name = path_parts[-1] if path_parts else None
    formatted_folder_name = re_sub(r'[<>:"/\\|?*]', '_', folder_name) if folder_name else None
    if not formatted_folder_name:
        random_str = ''.join(random_choices(ascii_letters + digits, k=10))
        formatted_folder_name = f"folder_{random_str}"
    return formatted_folder_name

# Función para obtener el nombre del archivo de la URL
# example: https://www.fireload.com/XXXXXXXXXXXXXXXX/ok.zip?pt=WVZOTlN6azNWV1pCZUh3434667833434H6455HkVG9WTUtuZz0%3D
def get_filename_from_url(file_url):
    parsed_url = urlparse(file_url)
    path_parts = parsed_url.path.strip("/").split("/")
    return path_parts[-1] if path_parts else None

# Función auxiliar para crear carpetas
def create_folder_if_not_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)

# Función para crear la carpeta de destino basandose en la URL
# param: folder_url: URL de la carpeta
# example: C:\Users\Usuario\Downloads\folder_68ac0cd3a5f200b6
def create_destiny_folder_by_url(folder_url: str):
    folder_name = get_folder_from_url(folder_url)
    return create_destiny_folder(folder_name)

# Funcion para crear la carpeta de destino basandose un nombre
# param: folder_name: Nombre de la carpeta
def create_destiny_folder(folder_name: str):
    root_folder = os.path.abspath(".\downloads")
    create_folder_if_not_exists(root_folder)
    folder_destiny = os.path.join(root_folder, folder_name)
    create_folder_if_not_exists(folder_destiny)
    return folder_destiny

# Función para verificar si el archivo existe en la carpeta de destino
def exists_file(folder, filename):
    return os.path.exists(os.path.join(folder, filename))