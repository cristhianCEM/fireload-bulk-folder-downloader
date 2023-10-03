from re import sub as re_sub
from random import choices as random_choices
from urllib.parse import urlparse
from string import ascii_letters, digits

# Función para obtener y formatear el nombre de la carpeta de la URL
# o generar uno aleatorio si es invalido o Nulo
def get_folder_name_from_url(folder_url):
    parsed_url = urlparse(folder_url)
    path_parts = parsed_url.path.strip("/").split("/")
    folder_name = path_parts[-1] if path_parts else None
    formatted_folder_name = re_sub(r'[<>:"/\\|?*]', '_', folder_name) if folder_name else None
    if not formatted_folder_name:
        random_str = ''.join(random_choices(ascii_letters + digits, k=10))
        formatted_folder_name = f"folder_{random_str}"
    return formatted_folder_name