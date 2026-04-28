import os
import sys
import subprocess
import re
import shutil

# --- SETUP ---
def preparar_entorno():
    try:
        import yt_dlp
        # Para Spotify necesitamos extraer metadata, a veces ayuda tener 'spotdl' o similar, 
        # pero aquí usaremos búsqueda por texto para no complicarte con más librerías.
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])

preparar_entorno()
import yt_dlp

# --- FUNCIONES DE SOPORTE ---
def gestionar_archivos():
    archivos = {'que_busco.txt': '', 'black_list.txt': '# IDs o links a ignorar\n'}
    for nombre, contenido in archivos.items():
        if not os.path.exists(nombre):
            with open(nombre, 'w', encoding='utf-8') as f: f.write(contenido)
    with open('que_busco.txt', 'r', encoding='utf-8') as f:
        busquedas = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    with open('black_list.txt', 'r', encoding='utf-8') as f:
        blacklist = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    return busquedas, blacklist

def limpiar_texto(t):
    return re.sub(r'[\\/*?:"<>|]', '', str(t)).strip()

def auditar_y_extraer_links(info):
    score = 0
    alertas = []
    links = {"licencia": "No detectada", "social": []}
    desc = info.get('description', '') or ""
    
    if any(x in desc.lower() for x in ["content id", "claim", "reclamado", "copyright"]):
        score += 50
        alertas.append("SISTEMA DE RECLAMO ACTIVO")

    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', desc)
    for u in urls:
        u_l = u.lower()
        if any(x in u_l for x in ["license", "licencia", "creative", "legal"]):
            links["licencia"] = u
        elif any(x in u_l for x in ["spotify", "instagram", "patreon", "bandcamp", "paypal"]):
            links["social"].append(u)

    comments = info.get('comments', []) or []
    for c in comments[:40]:
        t = c.get('text', '').lower()
        if any(w in t for w in ["scam", "fake", "strike", "reclamo", "estafa"]):
            score += 25
            alertas.append(f"COMENTARIO ALERTA: {t[:30]}...")

    status = "SEGURO"
    if score >= 70: status = "PELIGRO/SCAMMER"
    elif score >= 30: status = "RIESGO MODERADO"
    
    return status, alertas, links

# --- LÓGICA DE PROCESAMIENTO ---
def ejecutar_sistema():
    busquedas, blacklist = gestionar_archivos()
    base_repo = 'REPOSITORIO_MUSICA'
    historial = 'descargados.txt'
    
    if not os.path.exists(base_repo): os.makedirs(base_repo)

    ydl_opts = {
        'default_search': 'ytsearch1',
        'format': 'bestaudio/best',
        'get_comments': True,
        'max_comments': 40,
        'download_archive': historial,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'outtmpl': {
            'default': f'{base_repo}/%(uploader)s/%(title)s.%(ext)s',
            'chapter': f'{base_repo}/%(uploader)s/%(title)s - %(section_title)s.%(ext)s'
        },
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'FFmpegSplitChapters', 'force_keyframes': True}
        ],
        'quiet': True,
        'no_warnings': True,
    }

    metadata_acumulada = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for item in busquedas:
            if any(b in item for b in blacklist): continue

            # --- PARCHE PARA SPOTIFY ---
            if "spotify.com" in item:
                print(f"🟢 Detectado link de Spotify, buscando en YouTube: {item}")
                # Buscamos el título/artista usando ytsearch
                item = f"ytsearch1:{item} audio" 

            print(f"🔎 Analizando: {item}")
            try:
                info = ydl.extract_info(item, download=True)
                if info is None: continue
                
                entradas = info.get('entries', [info])
                for entrada in entradas:
                    if not entrada: continue
                    
                    status, alertas, links = auditar_y_extraer_links(entrada)
                    titulo = limpiar_texto(entrada.get('title', 'Sin_Titulo'))
                    artista = limpiar_texto(entrada.get('uploader', 'Desconocido'))
                    genero = limpiar_texto(entrada.get('genre', 'Varios'))
                    
                    ruta_carpeta = os.path.join(base_repo, genero, artista)
                    if not os.path.exists(ruta_carpeta): os.makedirs(ruta_carpeta)
                    
                    with open(os.path.join(ruta_carpeta, f"{titulo}.md"), 'w', encoding='utf-8') as md:
                        md.write(f"# {titulo}\n\n| Info | Detalle |\n| :--- | :--- |\n")
                        md.write(f"| **Artista** | {artista} |\n| **Género** | {genero} |\n")
                        md.write(f"| **Estado** | {status} |\n| **Fuente** | [Link]({entrada.get('webpage_url')}) |\n")
                        md.write(f"| **Licencia** | {links['licencia']} |\n\n")
                        if links['social']:
                            md.write("### 🔗 Redes\n")
                            for s in links['social']: md.write(f"- {s}\n")
                    
                    metadata_acumulada.append({
                        't': titulo, 'a': artista, 'g': genero, 's': status, 
                        'l': links['licencia'], 'p': f"{genero}/{artista}/{titulo}.md"
                    })
                    print(f"   [{status}] {titulo[:40]}")
            except Exception as e:
                print(f"❌ No se pudo procesar: {item}")

    # README
    with open(os.path.join(base_repo, "README.md"), 'w', encoding='utf-8') as rd:
        rd.write("# 📂 Mi Repositorio de Música\n\n| Canción | Artista | Estado | Ficha |\n| :--- | :--- | :--- | :--- |\n")
        for i in metadata_acumulada:
            rd.write(f"| {i['t']} | {i['a']} | {i['s']} | [VER]({i['p']}) |\n")

if __name__ == "__main__":
    ejecutar_sistema()