from re import sub as re_sub
from random import choices as random_choices
from urllib.parse import urlparse
from string import ascii_letters, digits

# Función para obtener y formatear el nombre de la carpeta de la URL
# o generar uno aleatorio si es invalido o Nulo
def get_foldername_from_url(folder_url):
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
    file_name = path_parts[-1] if path_parts else None
    return file_name