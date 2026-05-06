# Auto-free-songs

## Descripción / Description

Este repositorio contiene scripts en Python para descargar canciones usando enlaces de canales de YouTube y leer playlists de Spotify convertidas a CSV. El objetivo es automatizar la descarga de música libre de derechos o contenido que ya poseas y para el cual tengas permiso.

This repository contains Python scripts to download songs using YouTube channel/video links and Spotify playlists converted to CSV. The goal is to automate music downloads for royalty-free content or content you already own and are allowed to download.

## Contenido principal / Main contents

- `free-songs.py`: script base para descargas desde enlaces directos o búsquedas básicas.
- `free-songs-v2.py`: versión mejorada con manejo adicional de datos y opciones de descarga.
- `free-songs-spotify-support.py`: lee archivos CSV de Spotify e intenta descargar los temas correspondientes desde YouTube.
- `free-support-spotify.py`: herramienta de soporte para procesar playlists o listas de canciones de Spotify.
- `REPOSITORIO_MUSICA/`: carpeta de salida donde se organizan las descargas.
- `REPOSITORIO_MUSICA/Varios/`: carpeta con créditos y múltiples artistas.

## Requisitos / Requirements

1. Python 3.8+ instalado.
2. Conexión a internet.
3. Dependencias de Python según el script (por ejemplo `pytube`, `youtube-dl`, `yt-dlp`, `pandas` o similares). Estas no están incluidas en el repositorio, así que instala solo las necesarias para tu script.

## Instalación rápida / Quick setup

1. Clona o descarga este repositorio.
2. Crea un entorno virtual (recomendado):

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

3. Instala las librerías necesarias para tu script, por ejemplo:

```bash
pip install yt-dlp pandas
```

> Ajusta las dependencias según los scripts que uses.

## Uso general / Usage

### 1. Ejecutar el script principal

```bash
python free-songs.py
```

o

```bash
python free-songs-v2.py
```

Estos scripts intentan descargar canciones usando URLs de YouTube o datos que encuentren en archivos de entrada.

### 2. Usar soporte de Spotify / Spotify CSV

Si quieres generar un CSV desde Spotify, necesitas exportar tu playlist primero. Una opción recomendada es:

- https://www.chosic.com/spotify-playlist-exporter/

Después, guarda el CSV en el proyecto y ejecuta:

```bash
python free-songs-spotify-support.py
```

o

```bash
python free-support-spotify.py
```

Estos scripts leen las canciones desde el CSV y buscan el título/artist en YouTube para descargar.

### 3. Archivos de estado / Status files

El repositorio mantiene estos archivos para evitar descargas repetidas y conservar auditorías:

- `descargados.txt`
- `auditoria_total.txt`
- `REPORTE_AUDITORIA.txt`

No los elimines si quieres llevar control de lo descargado.

## Estructura de carpetas / Folder structure

- `REPOSITORIO_MUSICA/`: contiene las descargas organizadas por artista o canal.
- `REPOSITORIO_MUSICA/Varios/`: carpeta permitida con créditos y música variada.
- `que_busco.txt`: lista personal de búsquedas, no se sube por Git si está marcada en `.gitignore`.
- `black_list.txt`: lista de exclusiones personales.

## Notas importantes / Important notes

- Este proyecto no es responsable por el uso indebido de las descargas.
- Usa los scripts solo con contenido de libre distribución o con los permisos correspondientes.
- Algunos navegadores o herramientas pueden fallar en descargas largas; si el proceso se queda en 99%, reinicia o ejecuta el script de nuevo.

## Licencia / License

El código es de uso personal y de prueba. Incluye variables y reglas de exclusión para proteger datos privados y evitar subir listas personales a Git.

## Créditos / Credits

La carpeta `REPOSITORIO_MUSICA/Varios/` contiene créditos de artistas y debe permitirse en el repositorio según las necesidades del proyecto.
