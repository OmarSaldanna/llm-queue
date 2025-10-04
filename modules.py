import psycopg2
import requests
import tiktoken
import os
import urllib3
from dotenv import load_dotenv

# Deshabilitar advertencias de SSL (no recomendado para producción sin un certificado válido)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Colores para la consola ---
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# --- Conexión a la Base de Datos ---
def get_db_connection():
    """Establece y devuelve una conexión a la base de datos PostgreSQL."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except psycopg2.Error as e:
        print(f"{Colors.RED}Error al conectar con PostgreSQL: {e}{Colors.END}")
        return None

# --- Interacción con el LLM ---
def get_llm_response(prompt):
    """Envía un prompt al LLM y devuelve la respuesta."""
    url = os.getenv("LLM_API_URL")
    api_key = os.getenv("LLM_API_KEY")
    
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    system_prompt = "You are a helpful assistant."
    full_prompt = f"{system_prompt} {prompt}"
    
    data = {"prompt": full_prompt, "max_tokens": 4096, "temperature": 0.5}

    try:
        response = requests.post(url, headers=headers, json=data, verify=False, timeout=600) # Timeout de 10 minutos
        response.raise_for_status()
        return response.json()['content']
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Error en la petición al LLM: {e}{Colors.END}")
        return None

# --- Conteo de Tokens ---
def count_tokens(text):
    """Cuenta el número de tokens en un texto usando el codificador de GPT-4."""
    try:
        # Usamos el encoder para modelos como gpt-4 y gpt-3.5-turbo
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception as e:
        print(f"{Colors.YELLOW}Advertencia: No se pudo contar tokens. {e}{Colors.END}")
        return 0