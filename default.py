# D:\MediaCenter\Kodi\Addon\default.py
import os
import sys
import json
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

# Configurações do addon
addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
addon_version = addon.getAddonInfo('version')
addon_path = addon.getAddonInfo('path')
addon_handle = int(sys.argv[1])

# Caminhos
db_path = "D:\\MediaCenter\\Data\\media.db"
resources_path = os.path.join(addon_path, 'resources')
images_path = os.path.join(resources_path, 'images')

def log(message, level=xbmc.LOGINFO):
    """Log messages para debug"""
    xbmc.log(f"{addon_id} - {message}", level)

def load_media_data():
    """Carrega dados do Media Center"""
    try:
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            show_notification("Database não encontrado! Execute o scan primeiro.")
            return []
    except Exception as e:
        log(f"Erro ao carregar dados: {str(e)}", xbmc.LOGERROR)
        return []

def show_notification(message, time=5000):
    """Mostra notificação no Kodi"""
    xbmcgui.Dialog().notification(addon_name, message, time=time)

def create_list_item(label, path, is_folder=False, info=None, art=None):
    """Cria um item de lista para o Kodi"""
    list_item = xbmcgui.ListItem(label=label, path=path)
    list_item.setProperty('IsPlayable', 'false' if is_folder else 'true')
    
    if info:
        list_item.setInfo('video', info)
    
    if art:
        list_item.setArt(art)
    else:
        # Arte padrão baseada no tipo de conteúdo
        default_art = {
            'icon': os.path.join(images_path, 'icon.png'),
            'fanart': os.path.join(images_path, 'fanart.jpg')
        }
        list_item.setArt(default_art)
    
    if not is_folder:
        list_item.setContentLookup(False)
        
    return list_item

def main_menu():
    """Menu principal do addon"""
    items = [
        {
            'label': '🎬 Filmes',
            'action': 'list_movies',
            'folder': True,
            'art': {'icon': os.path.join(images_path, 'movies.png')}
        },
        {
            'label': '📺 Séries',
            'action': 'list_series',
            'folder': True,
            'art': {'icon': os.path.join(images_path, 'series.png')}
        },
        {
            'label': '🎌 Animes',
            'action': 'list_animes',
            'folder': True,
            'art': {'icon': os.path.join(images_path, 'anime.png')}
        },
        {
            'label': '📚 Biblioteca Completa',
            'action': 'list_all',
            'folder': True,
            'art': {'icon': os.path.join(images_path, 'library.png')}
        },
        {
            'label': '🔄 Atualizar Biblioteca',
            'action': 'update_library',
            'folder': False,
            'art': {'icon': os.path.join(images_path, 'refresh.png')}
        },
        {
            'label': 'ℹ️ Informações',
            'action': 'show_info',
            'folder': False,
            'art': {'icon': os.path.join(images_path, 'info.png')}
        }
    ]
    
    for item in items:
        list_item = create_list_item(
            label=item['label'],
            path=f"plugin://{addon_id}/?action={item['action']}",
            is_folder=item['folder'],
            art=item['art']
        )
        
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=list_item.getPath(),
            listitem=list_item,
            isFolder=item['folder']
        )
    
    xbmcplugin.endOfDirectory(addon_handle)
    xbmcplugin.setContent(addon_handle, 'files')

def list_movies():
    """Lista todos os filmes"""
    data = load_media_data()
    movies = [item for item in data if item.get('Type') == 'Filme']
    
    if not movies:
        show_notification("Nenhum filme encontrado!")
        xbmcplugin.endOfDirectory(addon_handle)
        return
    
    for movie in movies:
        title = movie.get('Name', 'Filme Desconhecido')
        file_path = movie.get('Path', '')
        size = movie.get('Size', 'N/A')
        
        info = {
            'title': title,
            'plot': f"Tamanho: {size}\nCaminho: {file_path}",
            'mediatype': 'movie'
        }
        
        art = {
            'icon': os.path.join(images_path, 'movie.png'),
            'poster': os.path.join(images_path, 'movie.png')
        }
        
        list_item = create_list_item(
            label=title,
            path=file_path,
            is_folder=False,
            info=info,
            art=art
        )
        
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=file_path,
            listitem=list_item,
            isFolder=False
        )
    
    xbmcplugin.endOfDirectory(addon_handle)
    xbmcplugin.setContent(addon_handle, 'movies')

def list_series():
    """Lista séries agrupadas"""
    data = load_media_data()
    series_episodes = [item for item in data if item.get('Type') == 'Série']
    
    if not series_episodes:
        show_notification("Nenhuma série encontrada!")
        xbmcplugin.endOfDirectory(addon_handle)
        return
    
    # Agrupar por série
    series_dict = {}
    for episode in series_episodes:
        series_name = episode.get('Series', 'Série Desconhecida')
        if series_name not in series_dict:
            series_dict[series_name] = []
        series_dict[series_name].append(episode)
    
    for series_name, episodes in series_dict.items():
        # Item da série (pasta)
        series_info = {
            'title': series_name,
            'plot': f"{len(episodes)} episódios disponíveis",
            'mediatype': 'tvshow'
        }
        
        series_art = {
            'icon': os.path.join(images_path, 'series.png'),
            'poster': os.path.join(images_path, 'series.png')
        }
        
        series_item = create_list_item(
            label=f"📺 {series_name} ({len(episodes)} episódios)",
            path=f"plugin://{addon_id}/?action=list_series_episodes&series={series_name}",
            is_folder=True,
            info=series_info,
            art=series_art
        )
        
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=series_item.getPath(),
            listitem=series_item,
            isFolder=True
        )
    
    xbmcplugin.endOfDirectory(addon_handle)
    xbmcplugin.setContent(addon_handle, 'tvshows')

def list_series_episodes(series_name):
    """Lista episódios de uma série específica"""
    data = load_media_data()
    episodes = [item for item in data if item.get('Type') == 'Série' and item.get('Series') == series_name]
    
    for episode in episodes:
        episode_name = episode.get('Episode', 'Episódio Desconhecido')
        file_path = episode.get('Path', '')
        size = episode.get('Size', 'N/A')
        
        info = {
            'title': episode_name,
            'tvshowtitle': series_name,
            'plot': f"Tamanho: {size}\nSérie: {series_name}",
            'mediatype': 'episode'
        }
        
        art = {
            'icon': os.path.join(images_path, 'episode.png')
        }
        
        list_item = create_list_item(
            label=episode_name,
            path=file_path,
            is_folder=False,
            info=info,
            art=art
        )
        
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=file_path,
            listitem=list_item,
            isFolder=False
        )
    
    xbmcplugin.endOfDirectory(addon_handle)
    xbmcplugin.setContent(addon_handle, 'episodes')

def list_animes():
    """Lista animes agrupados"""
    data = load_media_data()
    anime_episodes = [item for item in data if item.get('Type') == 'Anime']
    
    if not anime_episodes:
        show_notification("Nenhum anime encontrado!")
        xbmcplugin.endOfDirectory(addon_handle)
        return
    
    # Agrupar por anime
    anime_dict = {}
    for episode in anime_episodes:
        anime_name = episode.get('Anime', 'Anime Desconhecido')
        if anime_name not in anime_dict:
            anime_dict[anime_name] = []
        anime_dict[anime_name].append(episode)
    
    for anime_name, episodes in anime_dict.items():
        anime_info = {
            'title': anime_name,
            'plot': f"{len(episodes)} episódios disponíveis",
            'mediatype': 'tvshow'
        }
        
        anime_art = {
            'icon': os.path.join(images_path, 'anime.png'),
            'poster': os.path.join(images_path, 'anime.png')
        }
        
        anime_item = create_list_item(
            label=f"🎌 {anime_name} ({len(episodes)} episódios)",
            path=f"plugin://{addon_id}/?action=list_anime_episodes&anime={anime_name}",
            is_folder=True,
            info=anime_info,
            art=anime_art
        )
        
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=anime_item.getPath(),
            listitem=anime_item,
            isFolder=True
        )
    
    xbmcplugin.endOfDirectory(addon_handle)
    xbmcplugin.setContent(addon_handle, 'tvshows')

def list_anime_episodes(anime_name):
    """Lista episódios de um anime específico"""
    data = load_media_data()
    episodes = [item for item in data if item.get('Type') == 'Anime' and item.get('Anime') == anime_name]
    
    for episode in episodes:
        episode_name = episode.get('Episode', 'Episódio Desconhecido')
        file_path = episode.get('Path', '')
        size = episode.get('Size', 'N/A')
        
        info = {
            'title': episode_name,
            'tvshowtitle': anime_name,
            'plot': f"Tamanho: {size}\nAnime: {anime_name}",
            'mediatype': 'episode'
        }
        
        art = {
            'icon': os.path.join(images_path, 'anime_episode.png')
        }
        
        list_item = create_list_item(
            label=episode_name,
            path=file_path,
            is_folder=False,
            info=info,
            art=art
        )
        
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=file_path,
            listitem=list_item,
            isFolder=False
        )
    
    xbmcplugin.endOfDirectory(addon_handle)
    xbmcplugin.setContent(addon_handle, 'episodes')

def list_all():
    """Lista toda a biblioteca"""
    data = load_media_data()
    
    for item in data:
        if item.get('Type') == 'Filme':
            title = f"🎬 {item.get('Name')}"
            info = {'title': item.get('Name'), 'mediatype': 'movie'}
        elif item.get('Type') == 'Série':
            title = f"📺 {item.get('Series')} - {item.get('Episode')}"
            info = {'title': item.get('Episode'), 'tvshowtitle': item.get('Series'), 'mediatype': 'episode'}
        else:  # Anime
            title = f"🎌 {item.get('Anime')} - {item.get('Episode')}"
            info = {'title': item.get('Episode'), 'tvshowtitle': item.get('Anime'), 'mediatype': 'episode'}
        
        list_item = create_list_item(
            label=title,
            path=item.get('Path'),
            is_folder=False,
            info=info
        )
        
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=item.get('Path'),
            listitem=list_item,
            isFolder=False
        )
    
    xbmcplugin.endOfDirectory(addon_handle)
    xbmcplugin.setContent(addon_handle, 'files')

def update_library():
    """Executa scan do Media Center"""
    try:
        import subprocess
        script_path = "D:\\MediaCenter\\Scripts\\MediaCenterAddon.ps1"
        if os.path.exists(script_path):
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path, "scan"], 
                         capture_output=True, text=True)
            show_notification("Biblioteca atualizada com sucesso!")
        else:
            show_notification("Script do Media Center não encontrado!")
    except Exception as e:
        log(f"Erro ao atualizar biblioteca: {str(e)}", xbmc.LOGERROR)
        show_notification("Erro ao atualizar biblioteca!")

def show_info():
    """Mostra informações do addon"""
    data = load_media_data()
    total_items = len(data)
    movies = len([item for item in data if item.get('Type') == 'Filme'])
    series = len([item for item in data if item.get('Type') == 'Série'])
    animes = len([item for item in data if item.get('Type') == 'Anime'])
    
    message = f"""Media Center v{addon_version}

Biblioteca:
• Total de itens: {total_items}
• Filmes: {movies}
• Séries: {series}
• Animes: {animes}

Localização: D:\MediaCenter\
Database: {db_path}"""
    
    xbmcgui.Dialog().textviewer('Informações do Media Center', message)

def router(paramstring):
    """Roteamento de ações"""
    params = dict(paramstring.split('=') for param in paramstring.split('&') if '=' in param)
    
    action = params.get('action', 'main')
    series_name = params.get('series', '')
    anime_name = params.get('anime', '')
    
    if action == 'main':
        main_menu()
    elif action == 'list_movies':
        list_movies()
    elif action == 'list_series':
        list_series()
    elif action == 'list_series_episodes':
        list_series_episodes(series_name)
    elif action == 'list_animes':
        list_animes()
    elif action == 'list_anime_episodes':
        list_anime_episodes(anime_name)
    elif action == 'list_all':
        list_all()
    elif action == 'update_library':
        update_library()
    elif action == 'show_info':
        show_info()

if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
