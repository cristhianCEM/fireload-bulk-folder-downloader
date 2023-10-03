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
# estilo  https://www.fireload.com/68ac0cd3a5f200b6/OP-503.zip?pt=WVZOTlN6azNWV1pCZUhkUFNVTTBkMjlqTW5oNVp6MDlPcDlSZnVDdnlGUUJrc2JkVG9WTUtuZz0%3D
def get_filename_from_url(file_url):
    parsed_url = urlparse(file_url)
    path_parts = parsed_url.path.strip("/").split("/")
    return path_parts[-1] if path_parts else None

# Función para crear la carpeta de destino
# estilo  C:\Users\Usuario\Downloads\folder_68ac0cd3a5f200b6
def create_destiny_folder(folder_url):
    root_folder = os.path.abspath(".\downloads")
    if not os.path.exists(root_folder):
        os.mkdir(root_folder)
    folder = get_folder_from_url(folder_url)
    folder_destiny = os.path.join(root_folder, folder)
    if not os.path.exists(folder_destiny):
        os.mkdir(folder_destiny)
    return folder_destiny

# Función para verificar si el archivo existe en la carpeta de destino
def exists_file(folder, filename):
    return os.path.exists(os.path.join(folder, filename))