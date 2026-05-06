import os
import sys
import subprocess
import re
import shutil
from concurrent.futures import ThreadPoolExecutor

# --- 1. SETUP DE DEPENDENCIAS (Añadido requests y bs4 para Spotify) ---
def preparar_entorno():
    try:
        import yt_dlp
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp", "requests", "beautifulsoup4"])

preparar_entorno()
import yt_dlp
import requests
from bs4 import BeautifulSoup

# --- 2. CONFIGURACIÓN ---
BASE_REPO = 'REPOSITORIO_MUSICA'
HISTORIAL = 'descargados.txt'
MAX_HILOS = 4 

def gestionar_archivos():
    for nombre in ['que_busco.txt', 'black_list.txt']:
        if not os.path.exists(nombre):
            with open(nombre, 'w', encoding='utf-8') as f: f.write('')
    
    with open('que_busco.txt', 'r', encoding='utf-8') as f:
        busquedas = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    with open('black_list.txt', 'r', encoding='utf-8') as f:
        blacklist = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    return busquedas, blacklist

# --- 3. TRADUCTOR DE SPOTIFY A TEXTO ---
def obtener_metadatos_spotify(url):
    """Extrae 'Artista - Canción' de un link de Spotify para buscarlo en YT."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200: return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Buscamos el título de la página (ej: "Song Name - Song by Artist | Spotify")
        titulo_raw = soup.find('title').get_text()
        
        # Limpieza básica para obtener solo "Cancion - Artista"
        meta = titulo_raw.replace('| Spotify', '').replace('song by', '-').strip()
        return meta
    except Exception as e:
        print(f"⚠️ Error al leer Spotify: {e}")
        return None

# --- 4. AUDITORÍA ---
def limpiar_nombre(t):
    return re.sub(r'[\\/*?:"<>|]', '', str(t)).strip()

def auditar_y_extraer_links(info):
    score = 0
    links = {"licencia": "No detectada", "social": []}
    desc = info.get('description', '') or ""
    
    if any(x in desc.lower() for x in ["content id", "claim", "copyright"]): score += 50
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', desc)
    for u in urls:
        if any(x in u.lower() for x in ["license", "creative", "legal"]): links["licencia"] = u
        elif any(x in u.lower() for x in ["instagram", "patreon", "spotify"]): links["social"].append(u)
    
    status = "SEGURO" if score < 30 else "RIESGO" if score < 70 else "PELIGRO"
    return status, links

# --- 5. TRABAJADOR DE HILO ---
def procesar_tarea(item):
    busqueda_final = item
    
    # Si es Spotify, convertimos el link a texto de búsqueda
    if "spotify.com" in item:
        print(f"🟢 Traduciendo Spotify: {item}")
        meta_spoti = obtener_metadatos_spotify(item)
        if meta_spoti:
            busqueda_final = f"ytsearch1:{meta_spoti} lyrics"
        else:
            print(f"❌ No se pudo obtener info de Spotify para: {item}")
            return None

    ydl_opts = {
        'default_search': 'ytsearch1',
        'format': 'bestaudio/best',
        'download_archive': HISTORIAL,
        'outtmpl': f'{BASE_REPO}/temp_%(id)s.%(ext)s',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(busqueda_final, download=True)
            if info is None: return None
            
            entrada = info.get('entries', [info])[0]
            titulo = limpiar_nombre(entrada.get('title', 'Sin_Titulo'))
            artista = limpiar_nombre(entrada.get('uploader', 'Desconocido'))
            status, links = auditar_y_extraer_links(entrada)

            ruta_artista = os.path.join(BASE_REPO, artista)
            os.makedirs(ruta_artista, exist_ok=True)
            
            archivo_temp = os.path.join(BASE_REPO, f"temp_{entrada.get('id')}.mp3")
            archivo_final = os.path.join(ruta_artista, f"{titulo}.mp3")
            
            if os.path.exists(archivo_temp):
                shutil.move(archivo_temp, archivo_final)

            # Generar ficha MD
            with open(os.path.join(ruta_artista, f"{titulo}.md"), 'w', encoding='utf-8') as md:
                md.write(f"# {titulo}\n\n| Info | Detalle |\n| :--- | :--- |\n")
                md.write(f"| **Artista** | {artista} |\n| **Estado** | {status} |\n")
                md.write(f"| **Fuente** | [Link]({entrada.get('webpage_url')}) |\n")
                md.write(f"| **Licencia** | {links['licencia']} |\n")

            print(f"✅ Terminado: {titulo}")
            return {'t': titulo, 'a': artista, 's': status, 'l': links['licencia'], 'p': f"{artista}/{titulo}.md"}

        except Exception as e:
            print(f"❌ Error procesando {item}: {e}")
            return None

# --- 6. EJECUCIÓN ---
def ejecutar_sistema():
    busquedas, blacklist = gestionar_archivos()
    if not os.path.exists(BASE_REPO): os.makedirs(BASE_REPO)

    print(f"🚀 Iniciando motor MULTIHILO...")

    metadata_acumulada = []

    with ThreadPoolExecutor(max_workers=MAX_HILOS) as executor:
        tareas = [executor.submit(procesar_tarea, item) for item in busquedas if item not in blacklist]
        for t in tareas:
            res = t.result()
            if res: metadata_acumulada.append(res)

    with open(os.path.join(BASE_REPO, "README.md"), 'w', encoding='utf-8') as rd:
        rd.write("# 📂 Mi Biblioteca Auditada\n\n| Canción | Artista | Estado | Ficha |\n| :--- | :--- | :--- | :--- |\n")
        for i in metadata_acumulada:
            rd.write(f"| {i['t']} | {i['a']} | {i['s']} | [VER]({i['p']}) |\n")

if __name__ == "__main__":
    ejecutar_sistema()