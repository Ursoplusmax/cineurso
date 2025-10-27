import xbmcgui
import xbmcplugin
import xbmcaddon
import sys
import urllib.parse
import requests
import json

addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
base_url = sys.argv[0]

# Configurações TMDB
TMDB_API_KEY = "bf19c6b821a9beeb292567729c8bc45b"  # 👈 Obter em: https://www.themoviedb.org/settings/api
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

# Sua base de dados
DATABASE_URL = "https://raw.githubusercontent.com/Ursoplusmax/cineurso/main/database.json"

def get_url(**kwargs):
    return '{}?{}'.format(base_url, urllib.parse.urlencode(kwargs))

def get_tmdb_movies():
    """Busca filmes populares do TMDB"""
    try:
        url = f"{TMDB_BASE_URL}/movie/popular"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'pt-BR',
            'page': 1
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('results', [])
    except Exception as e:
        print(f"Erro TMDB: {e}")
    return []

def get_tmdb_series():
    """Busca séries populares do TMDB"""
    try:
        url = f"{TMDB_BASE_URL}/tv/popular"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'pt-BR',
            'page': 1
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('results', [])
    except Exception as e:
        print(f"Erro TMDB: {e}")
    return []

def search_tmdb(query, content_type="movie"):
    """Pesquisa no TMDB"""
    try:
        url = f"{TMDB_BASE_URL}/search/{content_type}"
        params = {
            'api_key': TMDB_API_KEY,
            'query': query,
            'language': 'pt-BR'
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('results', [])
    except Exception as e:
        print(f"Erro pesquisa TMDB: {e}")
    return []

def get_database_content():
    """Busca da sua base de dados"""
    try:
        response = requests.get(DATABASE_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"movies": [], "series": [], "animes": []}

def find_torrent_in_database(title, content_type="movie"):
    """Encontra torrent na base de dados"""
    db_content = get_database_content()
    
    if content_type == "movie":
        items = db_content.get('movies', [])
    else:
        items = db_content.get('series', [])
    
    # Busca por título similar
    for item in items:
        if title.lower() in item['title'].lower():
            return item
    
    return None

def list_main_categories():
    """Menu principal"""
    categories = [
        {'name': '🎬 FILMES POPULARES (TMDB)', 'type': 'tmdb_movies', 'icon': 'DefaultMovies.png'},
        {'name': '📺 SÉRIES POPULARES (TMDB)', 'type': 'tmdb_series', 'icon': 'DefaultTVShows.png'},
        {'name': '🔍 PESQUISAR NO TMDB', 'type': 'search_tmdb', 'icon': 'DefaultFolder.png'},
        {'name': '⚡ MEUS TORRENTS (Base Local)', 'type': 'local_torrents', 'icon': 'DefaultFavourites.png'},
        {'name': '🔄 ATUALIZAR CONTEÚDO', 'type': 'update', 'icon': 'DefaultSettings.png'}
    ]
    
    for cat in categories:
        if cat['type'] == 'tmdb_movies':
            url = get_url(action='list_tmdb_movies')
        elif cat['type'] == 'tmdb_series':
            url = get_url(action='list_tmdb_series')
        elif cat['type'] == 'search_tmdb':
            url = get_url(action='search_tmdb_menu')
        elif cat['type'] == 'local_torrents':
            url = get_url(action='list_local_torrents')
        else:
            url = get_url(action='update_content')
        
        li = xbmcgui.ListItem(cat['name'])
        li.setArt({'icon': cat['icon']})
        xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_tmdb_movies():
    """Lista filmes do TMDB"""
    movies = get_tmdb_movies()
    
    if not movies:
        li = xbmcgui.ListItem("Nenhum filme encontrado")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        for movie in movies:
            title = movie.get('title', '')
            year = movie.get('release_date', '')[:4]
            
            # Imagem
            poster_path = movie.get('poster_path')
            thumbnail = TMDB_IMAGE_URL + poster_path if poster_path else ""
            
            # Verificar se tem na base de dados
            torrent = find_torrent_in_database(title, "movie")
            
            if torrent:
                # Tem torrent - pode assistir
                magnet_url = f"plugin://plugin.video.elementum/play?uri={urllib.parse.quote(torrent['magnet'])}"
                display_title = f"▶ {title} ({year})"
                is_playable = True
            else:
                # Não tem torrent - mostrar info
                magnet_url = get_url(action='show_info', title=title, year=year, overview=movie.get('overview', ''))
                display_title = f"ℹ️ {title} ({year})"
                is_playable = False
            
            li = xbmcgui.ListItem(display_title)
            li.setArt({'thumb': thumbnail, 'icon': 'DefaultVideo.png'})
            li.setInfo('video', {
                'title': title,
                'year': int(year) if year else 0,
                'plot': movie.get('overview', ''),
                'rating': movie.get('vote_average', 0)
            })
            
            if is_playable:
                li.setProperty('IsPlayable', 'true')
            
            xbmcplugin.addDirectoryItem(addon_handle, magnet_url, li, is_playable)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_tmdb_series():
    """Lista séries do TMDB"""
    series = get_tmdb_series()
    
    if not series:
        li = xbmcgui.ListItem("Nenhuma série encontrada")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        for show in series:
            title = show.get('name', '')
            year = show.get('first_air_date', '')[:4]
            
            # Imagem
            poster_path = show.get('poster_path')
            thumbnail = TMDB_IMAGE_URL + poster_path if poster_path else ""
            
            # Verificar se tem na base de dados
            torrent = find_torrent_in_database(title, "tv")
            
            if torrent:
                # Tem torrent - pode assistir
                magnet_url = f"plugin://plugin.video.elementum/play?uri={urllib.parse.quote(torrent['magnet'])}"
                display_title = f"▶ {title} ({year})"
                is_playable = True
            else:
                # Não tem torrent - mostrar info
                magnet_url = get_url(action='show_info', title=title, year=year, overview=show.get('overview', ''))
                display_title = f"ℹ️ {title} ({year})"
                is_playable = False
            
            li = xbmcgui.ListItem(display_title)
            li.setArt({'thumb': thumbnail, 'icon': 'DefaultVideo.png'})
            li.setInfo('video', {
                'title': title,
                'year': int(year) if year else 0,
                'plot': show.get('overview', ''),
                'rating': show.get('vote_average', 0)
            })
            
            if is_playable:
                li.setProperty('IsPlayable', 'true')
            
            xbmcplugin.addDirectoryItem(addon_handle, magnet_url, li, is_playable)
    
    xbmcplugin.endOfDirectory(addon_handle)

def search_tmdb_menu():
    """Menu de pesquisa"""
    categories = [
        {'name': '🔍 PESQUISAR FILMES', 'type': 'movie'},
        {'name': '🔍 PESQUISAR SÉRIES', 'type': 'tv'}
    ]
    
    for cat in categories:
        url = get_url(action='search_tmdb', content_type=cat['type'])
        li = xbmcgui.ListItem(cat['name'])
        li.setArt({'icon': 'DefaultFolder.png'})
        xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def search_tmdb(content_type):
    """Pesquisa no TMDB"""
    keyboard = xbmc.Keyboard('', f'Pesquisar {content_type}:')
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        query = keyboard.getText()
        if query:
            results = search_tmdb(query, content_type)
            
            if not results:
                li = xbmcgui.ListItem("Nenhum resultado encontrado")
                xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
            else:
                for item in results:
                    title = item.get('title') or item.get('name')
                    year = item.get('release_date', '')[:4] or item.get('first_air_date', '')[:4]
                    
                    poster_path = item.get('poster_path')
                    thumbnail = TMDB_IMAGE_URL + poster_path if poster_path else ""
                    
                    torrent = find_torrent_in_database(title, content_type)
                    
                    if torrent:
                        magnet_url = f"plugin://plugin.video.elementum/play?uri={urllib.parse.quote(torrent['magnet'])}"
                        display_title = f"▶ {title} ({year})"
                        is_playable = True
                    else:
                        magnet_url = get_url(action='show_info', title=title, year=year, overview=item.get('overview', ''))
                        display_title = f"ℹ️ {title} ({year})"
                        is_playable = False
                    
                    li = xbmcgui.ListItem(display_title)
                    li.setArt({'thumb': thumbnail, 'icon': 'DefaultVideo.png'})
                    li.setInfo('video', {
                        'title': title,
                        'year': int(year) if year else 0,
                        'plot': item.get('overview', '')
                    })
                    
                    if is_playable:
                        li.setProperty('IsPlayable', 'true')
                    
                    xbmcplugin.addDirectoryItem(addon_handle, magnet_url, li, is_playable)
            
            xbmcplugin.endOfDirectory(addon_handle)

def list_local_torrents():
    """Lista conteúdo direto da base de dados"""
    content = get_database_content()
    
    categories = [
        {'name': '🎬 FILMES', 'type': 'movies', 'items': content.get('movies', [])},
        {'name': '📺 SÉRIES', 'type': 'series', 'items': content.get('series', [])},
        {'name': '🐉 ANIMES', 'type': 'animes', 'items': content.get('animes', [])}
    ]
    
    for cat in categories:
        if cat['items']:
            url = get_url(action='list_local_items', category=cat['type'])
            li = xbmcgui.ListItem(f"{cat['name']} ({len(cat['items'])})")
            li.setArt({'icon': 'DefaultFolder.png'})
            xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_local_items(category):
    """Lista itens de uma categoria"""
    content = get_database_content()
    items = content.get(category, [])
    
    for item in items:
        magnet_url = f"plugin://plugin.video.elementum/play?uri={urllib.parse.quote(item['magnet'])}"
        
        display_name = f"▶ {item['title']}"
        if item.get('quality'):
            display_name += f" [{item['quality']}]"
        if item.get('audio'):
            display_name += f" ({item['audio']})"
        
        li = xbmcgui.ListItem(display_name)
        li.setProperty('IsPlayable', 'true')
        li.setInfo('video', {'title': item['title']})
        
        xbmcplugin.addDirectoryItem(addon_handle, magnet_url, li, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def show_info(title, year, overview):
    """Mostra informações do conteúdo"""
    xbmcgui.Dialog().ok(f"{title} ({year})", overview)
    list_main_categories()

def update_content():
    """Atualiza conteúdo"""
    xbmcgui.Dialog().notification('Cine Urso', 'Conteúdo atualizado!', xbmcgui.NOTIFICATION_INFO)
    list_main_categories()

def router():
    params = urllib.parse.parse_qs(sys.argv[2][1:])
    
    action = params.get('action', [''])[0]
    content_type = params.get('content_type', [''])[0]
    category = params.get('category', [''])[0]
    title = params.get('title', [''])[0]
    year = params.get('year', [''])[0]
    overview = params.get('overview', [''])[0]
    
    if not action:
        list_main_categories()
    elif action == 'list_tmdb_movies':
        list_tmdb_movies()
    elif action == 'list_tmdb_series':
        list_tmdb_series()
    elif action == 'search_tmdb_menu':
        search_tmdb_menu()
    elif action == 'search_tmdb':
        search_tmdb(content_type)
    elif action == 'list_local_torrents':
        list_local_torrents()
    elif action == 'list_local_items':
        list_local_items(category)
    elif action == 'show_info':
        show_info(title, year, overview)
    elif action == 'update_content':
        update_content()

if __name__ == '__main__':
    router()
