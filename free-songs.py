import os
import sys
import subprocess
import re

# --- CONFIGURACIÓN DE SEGURIDAD ---
# Instala/Actualiza yt-dlp automáticamente
def preparar():
    try:
        import yt_dlp
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
    except:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])

preparar()
import yt_dlp

def cargar_listas():
    # Archivo 1: Lo que quieres bajar
    if not os.path.exists('que_busco.txt'):
        with open('que_busco.txt', 'w', encoding='utf-8') as f:
            f.write("https://www.youtube.com/@lofigeek/videos\nLAKEY INSPIRED - Chill Day\n")
    
    # Archivo 2: Canales que quieres evitar (Blacklist)
    if not os.path.exists('black_list.txt'):
        with open('black_list.txt', 'w', encoding='utf-8') as f:
            f.write("# Pega aquí links de canales o IDs a ignorar\nhttps://www.youtube.com/watch?v=-DfHaOYeaqk\n")

    with open('que_busco.txt', 'r', encoding='utf-8') as f:
        busquedas = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    
    with open('black_list.txt', 'r', encoding='utf-8') as f:
        blacklist = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        
    return busquedas, blacklist

def auditoria(info):
    puntos_scam = 0
    alertas = []
    
    # 1. Escaneo de descripción
    desc = info.get('description', '').lower()
    if any(x in desc for x in ["content id", "copyright claim", "distrokid", "rights managed"]):
        puntos_scam += 50
        alertas.append("SISTEMA DE RECLAMO ACTIVO (Content ID)")

    # 2. Escaneo de comentarios (Crucial para detectar SCAMS)
    comments = info.get('comments', []) if info.get('comments') else []
    for c in comments[:40]:
        t = c.get('text', '').lower()
        if any(w in t for w in ["scam", "fake", "strike", "reclamo", "estafa", "copyrighted", "lied"]):
            puntos_scam += 20
            alertas.append(f"REPORTE USUARIO: {t[:30]}...")

    status = "LIMPIO"
    if puntos_scam >= 60: status = "SCAMMER/PELIGRO"
    elif puntos_scam >= 30: status = "SOSPECHOSO"
    
    return status, alertas

def ejecutar():
    busquedas, blacklist = cargar_listas()
    destino = 'Descargas_Auditadas'
    if not os.path.exists(destino): os.makedirs(destino)

    # El error de JS Runtime se mitiga forzando el cliente web/android
    ydl_opts = {
        'default_search': 'ytsearch1',
        'format': 'bestaudio/best',
        'get_comments': True,
        'max_comments': 40,
        'outtmpl': f'{destino}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'quiet': True,
        'no_warnings': True,
    }

    with open('reporte_final.txt', 'w', encoding='utf-8') as report:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for item in busquedas:
                if any(b in item for b in blacklist):
                    print(f"🚫 Saltando Blacklist: {item}")
                    continue

                print(f"🔎 Procesando: {item}")
                try:
                    meta = ydl.extract_info(item, download=True)
                    videos = meta.get('entries', [meta])
                    
                    for v in videos:
                        if not v: continue
                        status, alertas = auditoria(v)
                        report.write(f"TÍTULO: {v.get('title')}\nSTATUS: {status}\nALERTAS: {', '.join(alertas)}\nLINK: {v.get('webpage_url')}\n\n")
                        print(f"   [{status}] {v.get('title')[:40]}")
                        
                except Exception as e:
                    print(f"❌ Error en {item}")

if __name__ == "__main__":
    # NOTA: Instala Node.js en tu PC para quitar el aviso de JS Runtime permanentemente.
    ejecutar()