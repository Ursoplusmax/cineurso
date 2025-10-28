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

def log(msg, level=xbmc.LOGDEBUG):
    xbmc.log(f"[{addon_id}] {msg}", level)

def load_media_data():
    """Load media data from JSON database"""
    try:
        if os.path.exists(DB_PATH):
            with open(DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            show_notification("Database não encontrado! Execute o scan no Media Center.")
            return []
    except Exception as e:
        log(f"Error loading database: {str(e)}", xbmc.LOGERROR)
        show_notification("Erro ao carregar biblioteca!")
        return []

def show_notification(message):
    xbmcgui.Dialog().notification(addon_name, message)

def main_menu():
    """Main menu"""
    items = [
        ("🎬 Filmes", "movies"),
        ("📺 Séries", "series"), 
        ("🎌 Animes", "animes"),
        ("📚 Todos os Itens", "all"),
        ("🔄 Atualizar", "update"),
        ("ℹ️ Sobre", "about")
    ]
    
    for label, action in items:
        li = xbmcgui.ListItem(label)
        url = f"{addon_url}?action={action}"
        
        if action in ["movies", "series", "animes", "all"]:
            li.setProperty('IsPlayable', 'false')
            is_folder = True
        else:
            li.setProperty('IsPlayable', 'false') 
            is_folder = False
            
        xbmcplugin.addDirectoryItem(addon_handle, url, li, is_folder)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_movies():
    """List all movies"""
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
            li.setInfo('video', {'title': title, 'mediatype': 'movie'})
            
            xbmcplugin.addDirectoryItem(addon_handle, path, li, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_series():
    """List series grouped by name"""
    data = load_media_data()
    series_data = [item for item in data if item.get('Type') == 'Série']
    
    if not series_data:
        li = xbmcgui.ListItem("Nenhuma série encontrada")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        # Group by series name
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
            xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_series_episodes(series_name):
    """List episodes for a specific series"""
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
            'mediatype': 'episode'
        })
        
        xbmcplugin.addDirectoryItem(addon_handle, path, li, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_animes():
    """List animes grouped by name"""
    data = load_media_data()
    anime_data = [item for item in data if item.get('Type') == 'Anime']
    
    if not anime_data:
        li = xbmcgui.ListItem("Nenhum anime encontrado")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        # Group by anime name
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
            xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_anime_episodes(anime_name):
    """List episodes for a specific anime"""
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
            'mediatype': 'episode'
        })
        
        xbmcplugin.addDirectoryItem(addon_handle, path, li, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_all():
    """List all media items"""
    data = load_media_data()
    
    for item in data:
        if item.get('Type') == 'Filme':
            label = f"🎬 {item.get('Name')}"
        elif item.get('Type') == 'Série':
            label = f"📺 {item.get('Series')} - {item.get('Episode')}"
        else:  # Anime
            label = f"🎌 {item.get('Anime')} - {item.get('Episode')}"
        
        path = item.get('Path', '')
        li = xbmcgui.ListItem(label)
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(addon_handle, path, li, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def update_library():
    """Update media library"""
    try:
        import subprocess
        script_path = "D:\\MediaCenter\\Scripts\\MediaCenterAddon.ps1"
        if os.path.exists(script_path):
            result = subprocess.run([
                "powershell", "-ExecutionPolicy", "Bypass", 
                "-File", script_path, "scan"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                show_notification("Biblioteca atualizada com sucesso!")
            else:
                show_notification("Erro ao atualizar biblioteca!")
        else:
            show_notification("Script do Media Center não encontrado!")
    except Exception as e:
        log(f"Update error: {str(e)}", xbmc.LOGERROR)
        show_notification("Erro na atualização!")

def show_about():
    """Show about information"""
    data = load_media_data()
    total = len(data)
    movies = len([x for x in data if x.get('Type') == 'Filme'])
    series = len([x for x in data if x.get('Type') == 'Série'])
    animes = len([x for x in data if x.get('Type') == 'Anime'])
    
    text = f"""Media Center v{addon.getAddonInfo('version')}

Estatísticas da Biblioteca:
• Total de itens: {total}
• Filmes: {movies}
• Séries: {series} 
• Animes: {animes}

Localização: D:\\MediaCenter\\
Desenvolvido para Kodi"""
    
    xbmcgui.Dialog().textviewer('Sobre o Media Center', text)

def router(paramstring):
    """Route actions"""
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
    elif action == 'about':
        show_about()

if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
