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

# Database path - DRIVE D
DB_PATH = "D:\\MediaCenter\\Data\\media.db"

def log(message, level=xbmc.LOGINFO):
    """Log messages para debug"""
    xbmc.log(f"{addon_id} - {message}", level)

def show_notification(message, time=3000):
    """Mostra notificação no Kodi"""
    xbmcgui.Dialog().notification(addon_name, message, time=time)

def load_media_data():
    """Carrega dados do database JSON"""
    try:
        if os.path.exists(DB_PATH):
            with open(DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                log(f"Database carregado: {len(data)} itens")
                return data
        else:
            log("Database não encontrado. Execute o scan primeiro.")
            show_notification("Database não encontrado! Execute o scan.")
            return []
    except Exception as e:
        log(f"Erro ao carregar database: {str(e)}", xbmc.LOGERROR)
        show_notification("Erro ao carregar biblioteca!")
        return []

def create_list_item(label, path, is_folder=False, info=None):
    """Cria item de lista padronizado"""
    list_item = xbmcgui.ListItem(label=label, path=path)
    list_item.setProperty('IsPlayable', 'false' if is_folder else 'true')
    
    if info:
        list_item.setInfo('video', info)
    
    # Arte padrão
    list_item.setArt({
        'icon': os.path.join(addon.getAddonInfo('path'), 'resources', 'images', 'icon.png'),
        'fanart': os.path.join(addon.getAddonInfo('path'), 'resources', 'images', 'fanart.jpg')
    })
    
    return list_item

def main_menu():
    """Menu principal do addon"""
    items = [
        {
            'label': '🎬 Filmes',
            'action': 'list_movies',
            'folder': True,
            'info': {'title': 'Filmes', 'plot': 'Biblioteca de filmes'}
        },
        {
            'label': '📺 Séries', 
            'action': 'list_series',
            'folder': True,
            'info': {'title': 'Séries', 'plot': 'Biblioteca de séries'}
        },
        {
            'label': '🎌 Animes',
            'action': 'list_animes', 
            'folder': True,
            'info': {'title': 'Animes', 'plot': 'Biblioteca de animes'}
        },
        {
            'label': '📚 Biblioteca Completa',
            'action': 'list_all',
            'folder': True,
            'info': {'title': 'Todos os Itens', 'plot': 'Toda a biblioteca'}
        },
        {
            'label': '🔄 Atualizar Biblioteca',
            'action': 'update_library',
            'folder': False,
            'info': {'title': 'Atualizar', 'plot': 'Escanear biblioteca'}
        },
        {
            'label': '📊 Estatísticas',
            'action': 'show_stats',
            'folder': False, 
            'info': {'title': 'Estatísticas', 'plot': 'Estatísticas da biblioteca'}
        },
        {
            'label': 'ℹ️ Sobre',
            'action': 'show_about',
            'folder': False,
            'info': {'title': 'Sobre', 'plot': 'Informações do addon'}
        }
    ]
    
    for item in items:
        list_item = create_list_item(
            label=item['label'],
            path=f"{addon_url}?action={item['action']}",
            is_folder=item['folder'],
            info=item['info']
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
        list_item = create_list_item("Nenhum filme encontrado", "")
        xbmcplugin.addDirectoryItem(addon_handle, "", list_item, False)
    else:
        for movie in movies:
            title = movie.get('Name', 'Filme Desconhecido')
            path = movie.get('Path', '')
            size = movie.get('Size', 'N/A')
            
            info = {
                'title': title,
                'plot': f"Tamanho: {size}",
                'mediatype': 'movie'
            }
            
            list_item = create_list_item(
                label=f"🎬 {title}",
                path=path,
                is_folder=False,
                info=info
            )
            
            xbmcplugin.addDirectoryItem(addon_handle, path, list_item, False)
    
    xbmcplugin.setContent(addon_handle, 'movies')
    xbmcplugin.endOfDirectory(addon_handle)

def list_series():
    """Lista séries agrupadas"""
    data = load_media_data()
    series_data = [item for item in data if item.get('Type') == 'Série']
    
    if not series_data:
        list_item = create_list_item("Nenhuma série encontrada", "")
        xbmcplugin.addDirectoryItem(addon_handle, "", list_item, False)
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
            info = {
                'title': series_name,
                'plot': f"{len(episodes)} episódios disponíveis",
                'mediatype': 'tvshow'
            }
            
            list_item = create_list_item(
                label=label,
                path=f"{addon_url}?action=list_series_episodes&series={series_name}",
                is_folder=True,
                info=info
            )
            
            xbmcplugin.addDirectoryItem(addon_handle, list_item.getPath(), list_item, True)
    
    xbmcplugin.setContent(addon_handle, 'tvshows')
    xbmcplugin.endOfDirectory(addon_handle)

def list_series_episodes(series_name):
    """Lista episódios de uma série específica"""
    data = load_media_data()
    episodes = [item for item in data if item.get('Type') == 'Série' and item.get('Series') == series_name]
    
    for episode in episodes:
        episode_name = episode.get('Episode', 'Episódio Desconhecido')
        path = episode.get('Path', '')
        size = episode.get('Size', 'N/A')
        
        info = {
            'title': episode_name,
            'tvshowtitle': series_name,
            'plot': f"Série: {series_name}\nTamanho: {size}",
            'mediatype': 'episode'
        }
        
        list_item = create_list_item(
            label=episode_name,
            path=path,
            is_folder=False,
            info=info
        )
        
        xbmcplugin.addDirectoryItem(addon_handle, path, list_item, False)
    
    xbmcplugin.setContent(addon_handle, 'episodes')
    xbmcplugin.endOfDirectory(addon_handle)

def list_animes():
    """Lista animes agrupados"""
    data = load_media_data()
    anime_data = [item for item in data if item.get('Type') == 'Anime']
    
    if not anime_data:
        list_item = create_list_item("Nenhum anime encontrado", "")
        xbmcplugin.addDirectoryItem(addon_handle, "", list_item, False)
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
            info = {
                'title': anime_name,
                'plot': f"{len(episodes)} episódios disponíveis", 
                'mediatype': 'tvshow'
            }
            
            list_item = create_list_item(
                label=label,
                path=f"{addon_url}?action=list_anime_episodes&anime={anime_name}",
                is_folder=True,
                info=info
            )
            
            xbmcplugin.addDirectoryItem(addon_handle, list_item.getPath(), list_item, True)
    
    xbmcplugin.setContent(addon_handle, 'tvshows')
    xbmcplugin.endOfDirectory(addon_handle)

def list_anime_episodes(anime_name):
    """Lista episódios de um anime específico"""
    data = load_media_data()
    episodes = [item for item in data if item.get('Type') == 'Anime' and item.get('Anime') == anime_name]
    
    for episode in episodes:
        episode_name = episode.get('Episode', 'Episódio Desconhecido')
        path = episode.get('Path', '')
        size = episode.get('Size', 'N/A')
        
        info = {
            'title': episode_name,
            'tvshowtitle': anime_name,
            'plot': f"Anime: {anime_name}\nTamanho: {size}",
            'mediatype': 'episode'
        }
        
        list_item = create_list_item(
            label=episode_name,
            path=path,
            is_folder=False,
            info=info
        )
        
        xbmcplugin.addDirectoryItem(addon_handle, path, list_item, False)
    
    xbmcplugin.setContent(addon_handle, 'episodes')
    xbmcplugin.endOfDirectory(addon_handle)

def list_all():
    """Lista toda a biblioteca"""
    data = load_media_data()
    
    for item in data:
        if item.get('Type') == 'Filme':
            label = f"🎬 {item.get('Name')}"
            info = {'title': item.get('Name'), 'mediatype': 'movie'}
        elif item.get('Type') == 'Série':
            label = f"📺 {item.get('Series')} - {item.get('Episode')}"
            info = {'title': item.get('Episode'), 'tvshowtitle': item.get('Series'), 'mediatype': 'episode'}
        else:
            label = f"🎌 {item.get('Anime')} - {item.get('Episode')}"
            info = {'title': item.get('Episode'), 'tvshowtitle': item.get('Anime'), 'mediatype': 'episode'}
        
        path = item.get('Path', '')
        list_item = create_list_item(label, path, False, info)
        xbmcplugin.addDirectoryItem(addon_handle, path, list_item, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def update_library():
    """Atualiza biblioteca - VERSÃO OTIMIZADA"""
    try:
        # Usar scanner interno (mais confiável)
        from resources.lib import scanner
        
        progress = xbmcgui.DialogProgress()
        progress.create('Media Center', 'Iniciando scan da biblioteca...')
        
        # Executar scan
        success = scanner.scan_library()
        
        progress.close()
        
        if success:
            show_notification("✅ Biblioteca atualizada com sucesso!")
        else:
            show_notification("❌ Erro durante o scan!")
            
    except Exception as e:
        log(f"Erro no scan: {str(e)}", xbmc.LOGERROR)
        show_notification("❌ Erro ao executar scan!")

def show_stats():
    """Mostra estatísticas da biblioteca"""
    data = load_media_data()
    
    total = len(data)
    movies = len([x for x in data if x.get('Type') == 'Filme'])
    series = len([x for x in data if x.get('Type') == 'Série'])
    animes = len([x for x in data if x.get('Type') == 'Anime'])
    
    # Calcular tamanho total
    total_size = 0
    for item in data:
        try:
            size_str = item.get('Size', '0 GB')
            size_gb = float(size_str.replace(' GB', ''))
            total_size += size_gb
        except:
            pass
    
    text = f"""📊 ESTATÍSTICAS - MEDIA CENTER

Biblioteca:
• Total de itens: {total}
• Filmes: {movies}
• Séries: {series} 
• Animes: {animes}
• Espaço usado: {total_size:.2f} GB

Armazenamento:
• Drive D: {get_drive_space()}

Database: {DB_PATH}"""

    xbmcgui.Dialog().textviewer('Estatísticas do Media Center', text)

def get_drive_space():
    """Obtém espaço livre no drive D"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("D:\\")
        return f"{free // (2**30)} GB livres"
    except:
        return "N/A"

def show_about():
    """Mostra informações sobre o addon"""
    text = f"""🎬 MEDIA CENTER HD

Versão: {addon.getAddonInfo('version')}

Descrição:
Addon para gerenciar sua biblioteca de filmes, 
séries e animes no HD externo (Drive D).

Recursos:
• Interface integrada com Kodi
• Suporte a múltiplos formatos de vídeo
• Organização automática por categorias
• Scan rápido da biblioteca
• Estatísticas detalhadas

Desenvolvido para Kodi 19+ (Matrix)"""

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
    
    # Mapeamento de ações
    actions = {
        'main': main_menu,
        'movies': list_movies,
        'series': list_series,
        'list_series_episodes': lambda: list_series_episodes(params.get('series', '')),
        'animes': list_animes,
        'list_anime_episodes': lambda: list_anime_episodes(params.get('anime', '')),
        'all': list_all,
        'update_library': update_library,
        'show_stats': show_stats,
        'show_about': show_about
    }
    
    # Executar ação
    if action in actions:
        actions[action]()
    else:
        main_menu()

if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
