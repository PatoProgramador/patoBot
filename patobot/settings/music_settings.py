YDL_OPTIONS = {
    "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "extractaudio": False,  # No extraer, solo obtener URL
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "logtostderr": False,
    "ignoreerrors": False,
    "default_search": "auto",
    "source_address": "0.0.0.0",
    "prefer_ffmpeg": True,
    "keepvideo": False,
    "age_limit": None,
    # Evitar formatos problemáticos
    "format_sort": ["quality", "res", "fps", "hdr:12", "codec:vp9.2", "size", "br", "asr", "proto"],
    "format_sort_force": True,
}

# Opciones para FFmpeg con mejoras de conexión y manejo de HLS
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin -protocol_whitelist file,http,https,tcp,tls,crypto",
    "options": "-vn -filter:a 'volume=0.5' -bufsize 512k -maxrate 128k"
}