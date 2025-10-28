import os
import sys
import json
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

# Addon info
addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
addon_handle = int(sys.argv[1])
addon_url = sys.argv[0]

# Database path
DB_PATH = "D:\\MediaCenter\\Data\\media.db"

def log(message):
    xbmc.log(f"[{addon_id}] {message}", xbmc.LOGINFO)

def show_notification(message):
    xbmcgui.Dialog().notification(addon_name, message)

def load_media_data():
    """Carrega dados do database"""
    try:
        if os.path.exists(DB_PATH):
            with open(DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                log(f"Database carregado: {len(data)} itens")
                return data
        else:
            log("Database não encontrado")
            return []
    except Exception as e:
        log(f"Erro ao carregar database: {str(e)}")
        return []

def main_menu():
    """Menu principal"""
    items = [
        ("🎬 Filmes", "movies", True),
        ("📺 Séries", "series", True),
        ("🎌 Animes", "animes", True),
        ("📚 Biblioteca Completa", "all", True),
        ("🔄 Atualizar Biblioteca", "update", False),
        ("📊 Estatísticas", "stats", False),
        ("ℹ️ Sobre", "about", False)
    ]
    
    for label, action, is_folder in items:
        li = xbmcgui.ListItem(label)
        url = f"{addon_url}?action={action}"
        li.setProperty('IsPlayable', 'false')
        xbmcplugin.addDirectoryItem(addon_handle, url, li, is_folder)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_movies():
    """Lista todos os filmes"""
    data = load_media_data()
    movies = [item for item in data if item.get('Type') == 'Filme']
    
    if not movies:
        li = xbmcgui.ListItem("Nenhum filme encontrado")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        for movie in movies:
            title = movie.get('Name', 'Filme Desconhecido')
            path = movie.get('Path', '')
            
            li = xbmcgui.ListItem(title)
            li.setProperty('IsPlayable', 'true')
            li.setInfo('video', {
                'title': title,
                'plot': f"Tamanho: {movie.get('Size', 'N/A')}",
                'mediatype': 'movie'
            })
            
            xbmcplugin.addDirectoryItem(addon_handle, path, li, False)
    
    xbmcplugin.setContent(addon_handle, 'movies')
    xbmcplugin.endOfDirectory(addon_handle)

def list_series():
    """Lista séries agrupadas"""
    data = load_media_data()
    series_data = [item for item in data if item.get('Type') == 'Série']
    
    if not series_data:
        li = xbmcgui.ListItem("Nenhuma série encontrada")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        # Agrupar por série
        series_dict = {}
        for episode in series_data:
            series_name = episode.get('Series', 'Série Desconhecida')
            if series_name not in series_dict:
                series_dict[series_name] = []
            series_dict[series_name].append(episode)
        
        for series_name, episodes in series_dict.items():
            label = f"📺 {series_name} ({len(episodes)} episódios)"
            li = xbmcgui.ListItem(label)
            url = f"{addon_url}?action=series_episodes&series={series_name}"
            li.setInfo('video', {
                'title': series_name,
                'plot': f"{len(episodes)} episódios disponíveis",
                'mediatype': 'tvshow'
            })
            xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.setContent(addon_handle, 'tvshows')
    xbmcplugin.endOfDirectory(addon_handle)

def list_series_episodes(series_name):
    """Lista episódios de uma série"""
    data = load_media_data()
    episodes = [item for item in data if item.get('Type') == 'Série' and item.get('Series') == series_name]
    
    for episode in episodes:
        episode_name = episode.get('Episode', 'Episódio Desconhecido')
        path = episode.get('Path', '')
        
        li = xbmcgui.ListItem(episode_name)
        li.setProperty('IsPlayable', 'true')
        li.setInfo('video', {
            'title': episode_name,
            'tvshowtitle': series_name,
            'plot': f"Série: {series_name}\nTamanho: {episode.get('Size', 'N/A')}",
            'mediatype': 'episode'
        })
        
        xbmcplugin.addDirectoryItem(addon_handle, path, li, False)
    
    xbmcplugin.setContent(addon_handle, 'episodes')
    xbmcplugin.endOfDirectory(addon_handle)

def list_animes():
    """Lista animes agrupados"""
    data = load_media_data()
    anime_data = [item for item in data if item.get('Type') == 'Anime']
    
    if not anime_data:
        li = xbmcgui.ListItem("Nenhum anime encontrado")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        # Agrupar por anime
        anime_dict = {}
        for episode in anime_data:
            anime_name = episode.get('Anime', 'Anime Desconhecido')
            if anime_name not in anime_dict:
                anime_dict[anime_name] = []
            anime_dict[anime_name].append(episode)
        
        for anime_name, episodes in anime_dict.items():
            label = f"🎌 {anime_name} ({len(episodes)} episódios)"
            li = xbmcgui.ListItem(label)
            url = f"{addon_url}?action=anime_episodes&anime={anime_name}"
            li.setInfo('video', {
                'title': anime_name,
                'plot': f"{len(episodes)} episódios disponíveis",
                'mediatype': 'tvshow'
            })
            xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.setContent(addon_handle, 'tvshows')
    xbmcplugin.endOfDirectory(addon_handle)

def list_anime_episodes(anime_name):
    """Lista episódios de um anime"""
    data = load_media_data()
    episodes = [item for item in data if item.get('Type') == 'Anime' and item.get('Anime') == anime_name]
    
    for episode in episodes:
        episode_name = episode.get('Episode', 'Episódio Desconhecido')
        path = episode.get('Path', '')
        
        li = xbmcgui.ListItem(episode_name)
        li.setProperty('IsPlayable', 'true')
        li.setInfo('video', {
            'title': episode_name,
            'tvshowtitle': anime_name,
            'plot': f"Anime: {anime_name}\nTamanho: {episode.get('Size', 'N/A')}",
            'mediatype': 'episode'
        })
        
        xbmcplugin.addDirectoryItem(addon_handle, path, li, False)
    
    xbmcplugin.setContent(addon_handle, 'episodes')
    xbmcplugin.endOfDirectory(addon_handle)

def list_all():
    """Lista toda a biblioteca"""
    data = load_media_data()
    
    for item in data:
        if item.get('Type') == 'Filme':
            label = f"🎬 {item.get('Name')}"
            mediatype = 'movie'
        elif item.get('Type') == 'Série':
            label = f"📺 {item.get('Series')} - {item.get('Episode')}"
            mediatype = 'episode'
        else:
            label = f"🎌 {item.get('Anime')} - {item.get('Episode')}"
            mediatype = 'episode'
        
        path = item.get('Path', '')
        li = xbmcgui.ListItem(label)
        li.setProperty('IsPlayable', 'true')
        li.setInfo('video', {'mediatype': mediatype})
        xbmcplugin.addDirectoryItem(addon_handle, path, li, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def update_library():
    """Atualiza a biblioteca - VERSÃO CORRIGIDA"""
    try:
        import subprocess
        
        # Caminho do script PowerShell
        script_path = "D:\\MediaCenter\\Scripts\\MediaCenterAddon.ps1"
        
        if os.path.exists(script_path):
            # Comando corrigido para Kodi
            command = [
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-WindowStyle", "Hidden",
                "-File", script_path,
                "scan"
            ]
            
            # Executar sem esperar
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # Esconder janela
            
            subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo
            )
            
            show_notification("Scan iniciado... Verifique o log depois.")
            log("Scan iniciado via PowerShell")
            
        else:
            show_notification("Script não encontrado!")
            log(f"Script não encontrado: {script_path}")
            
    except Exception as e:
        log(f"Erro no update: {str(e)}")
        show_notification("Erro ao iniciar scan")

def show_statistics():
    """Mostra estatísticas"""
    data = load_media_data()
    
    total = len(data)
    movies = len([x for x in data if x.get('Type') == 'Filme'])
    series = len([x for x in data if x.get('Type') == 'Série'])
    animes = len([x for x in data if x.get('Type') == 'Anime'])
    
    text = f"""📊 ESTATÍSTICAS DO MEDIA CENTER

Biblioteca:
• Total de itens: {total}
• Filmes: {movies}
• Séries: {series}
• Animes: {animes}

Localização: D:\\MediaCenter\\
Database: {DB_PATH}"""

    xbmcgui.Dialog().textviewer('Estatísticas', text)

def show_about():
    """Mostra informações sobre"""
    text = f"""🎬 MEDIA CENTER HD

Versão: {addon.getAddonInfo('version')}

Recursos:
• Suporte a Filmes, Séries e Animes
• Drive D com 2TB de armazenamento
• Interface integrada com Kodi
• Scan automático de biblioteca

Desenvolvido para organizar sua coleção de mídia."""

    xbmcgui.Dialog().textviewer('Sobre o Media Center', text)

def router(paramstring):
    """Roteamento de ações"""
    params = {}
    if paramstring:
        for param in paramstring.split('&'):
            if '=' in param:
                key, value = param.split('=')
                params[key] = value
    
    action = params.get('action', 'main')
    
    if action == 'main':
        main_menu()
    elif action == 'movies':
        list_movies()
    elif action == 'series':
        list_series()
    elif action == 'series_episodes':
        list_series_episodes(params.get('series', ''))
    elif action == 'animes':
        list_animes()
    elif action == 'anime_episodes':
        list_anime_episodes(params.get('anime', ''))
    elif action == 'all':
        list_all()
    elif action == 'update':
        update_library()
    elif action == 'stats':
        show_statistics()
    elif action == 'about':
        show_about()

if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
