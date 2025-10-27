import xbmcgui
import xbmcplugin
import xbmcaddon
import sys
import urllib.parse
import requests
import json
import re

addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
base_url = sys.argv[0]

# Configurações
TMDB_API_KEY = "bf19c6b821a9beeb292567729c8bc45b"  # 👈 Obter em https://www.themoviedb.org/settings/api
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

# Sua base de dados com links torrent
DATABASE_URL = "https://raw.githubusercontent.com/Ursoplusmax/cineurso/main/database.json"

def get_url(**kwargs):
    return '{}?{}'.format(base_url, urllib.parse.urlencode(kwargs))

def get_tmdb_content(content_type, query=""):
    """Busca conteúdo do TMDB"""
    try:
        if query:
            # Busca por nome
            url = f"{TMDB_BASE_URL}/search/{content_type}"
            params = {
                'api_key': TMDB_API_KEY,
                'query': query,
                'language': 'pt-BR'
            }
        else:
            # Conteúdo popular
            if content_type == 'movie':
                url = f"{TMDB_BASE_URL}/movie/popular"
            else:
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

def get_torrent_sources(title, year="", content_type="movie"):
    """Busca fontes torrent para o conteúdo"""
    try:
        # Primeiro tenta da sua base de dados
        db_content = get_database_content()
        
        # Busca na base por título similar
        torrents = []
        if content_type == 'movie':
            items = db_content.get('movies', [])
        else:
            items = db_content.get('series', [])
        
        for item in items:
            if title.lower() in item['title'].lower():
                torrents.append(item)
        
        return torrents
        
    except Exception as e:
        print(f"Erro busca torrent: {e}")
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

def list_main_categories():
    """Menu principal"""
    categories = [
        {'name': '🎬 FILMES POPULARES', 'type': 'movie', 'icon': 'DefaultMovies.png'},
        {'name': '📺 SÉRIES POPULARES', 'type': 'tv', 'icon': 'DefaultTVShows.png'},
        {'name': '🔍 PESQUISAR', 'type': 'search', 'icon': 'DefaultFolder.png'},
        {'name': '⚡ MEUS TORRENTS', 'type': 'mytorrents', 'icon': 'DefaultFavourites.png'},
        {'name': '🔄 ATUALIZAR', 'type': 'update', 'icon': 'DefaultSettings.png'}
    ]
    
    for cat in categories:
        if cat['type'] in ['movie', 'tv']:
            url = get_url(action='list_tmdb', content_type=cat['type'])
        elif cat['type'] == 'search':
            url = get_url(action='search_menu')
        elif cat['type'] == 'mytorrents':
            url = get_url(action='list_database')
        else:
            url = get_url(action='update_content')
        
        li = xbmcgui.ListItem(cat['name'])
        li.setArt({'icon': cat['icon']})
        xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_tmdb_content(content_type):
    """Lista conteúdo do TMDB com capas"""
    items = get_tmdb_content(content_type)
    
    if not items:
        li = xbmcgui.ListItem("Nenhum conteúdo encontrado")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        for item in items:
            title = item.get('title') or item.get('name')
            year = item.get('release_date', '')[:4] or item.get('first_air_date', '')[:4]
            
            # Construir URL da imagem
            poster_path = item.get('poster_path')
            if poster_path:
                thumbnail = TMDB_IMAGE_URL + poster_path
                fanart = f"https://image.tmdb.org/t/p/w1280{item.get('backdrop_path', '')}"
            else:
                thumbnail = ""
                fanart = ""
            
            # Item para listar fontes torrent
            url = get_url(
                action='list_torrent_sources',
                title=title,
                year=year,
                content_type=content_type,
                tmdb_id=item.get('id')
            )
            
            li = xbmcgui.ListItem(f"{title} ({year})")
            li.setArt({
                'thumb': thumbnail,
                'poster': thumbnail,
                'fanart': fanart,
                'icon': 'DefaultVideo.png'
            })
            li.setInfo('video', {
                'title': title,
                'year': int(year) if year else 0,
                'plot': item.get('overview', ''),
                'rating': item.get('vote_average', 0)
            })
            
            xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_torrent_sources(title, year, content_type, tmdb_id):
    """Lista fontes torrent disponíveis"""
    torrents = get_torrent_sources(title, year, content_type)
    
    if not torrents:
        li = xbmcgui.ListItem("Nenhum torrent encontrado")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        for torrent in torrents:
            # Criar item playable
            magnet_url = f"plugin://plugin.video.elementum/play?uri={urllib.parse.quote(torrent['magnet'])}"
            
            display_name = f"{torrent['title']}"
            if torrent.get('quality'):
                display_name += f" [{torrent['quality']}]"
            if torrent.get('audio'):
                display_name += f" ({torrent['audio']})"
            if torrent.get('size'):
                display_name += f" - {torrent['size']}"
            
            li = xbmcgui.ListItem(display_name)
            li.setProperty('IsPlayable', 'true')
            li.setInfo('video', {
                'title': torrent['title'],
                'genre': ', '.join(torrent.get('genre', []))
            })
            
            xbmcplugin.addDirectoryItem(addon_handle, magnet_url, li, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def search_menu():
    """Menu de pesquisa"""
    categories = [
        {'name': '🔍 PESQUISAR FILMES', 'type': 'movie'},
        {'name': '🔍 PESQUISAR SÉRIES', 'type': 'tv'},
        {'name': '🔍 PESQUISAR ANIMES', 'type': 'anime'}
    ]
    
    for cat in categories:
        url = get_url(action='search', content_type=cat['type'])
        li = xbmcgui.ListItem(cat['name'])
        li.setArt({'icon': 'DefaultFolder.png'})
        xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def search_content(content_type):
    """Pesquisa conteúdo"""
    keyboard = xbmc.Keyboard('', f'Pesquisar {content_type}:')
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        query = keyboard.getText()
        if query:
            if content_type == 'anime':
                # Pesquisa direto na base de dados
                list_database_search(query)
            else:
                # Pesquisa no TMDB
                list_tmdb_search(content_type, query)

def list_tmdb_search(content_type, query):
    """Lista resultados da pesquisa TMDB"""
    items = get_tmdb_content(content_type, query)
    
    if not items:
        li = xbmcgui.ListItem("Nenhum resultado encontrado")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        for item in items:
            title = item.get('title') or item.get('name')
            year = item.get('release_date', '')[:4] or item.get('first_air_date', '')[:4]
            
            poster_path = item.get('poster_path')
            thumbnail = TMDB_IMAGE_URL + poster_path if poster_path else ""
            
            url = get_url(
                action='list_torrent_sources',
                title=title,
                year=year,
                content_type=content_type,
                tmdb_id=item.get('id')
            )
            
            li = xbmcgui.ListItem(f"{title} ({year})")
            li.setArt({'thumb': thumbnail, 'icon': 'DefaultVideo.png'})
            li.setInfo('video', {
                'title': title,
                'year': int(year) if year else 0,
                'plot': item.get('overview', '')
            })
            
            xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_database():
    """Lista conteúdo direto da base de dados"""
    content = get_database_content()
    
    categories = [
        {'name': '🎬 FILMES', 'type': 'movies', 'items': content.get('movies', [])},
        {'name': '📺 SÉRIES', 'type': 'series', 'items': content.get('series', [])},
        {'name': '🐉 ANIMES', 'type': 'animes', 'items': content.get('animes', [])}
    ]
    
    for cat in categories:
        if cat['items']:
            url = get_url(action='list_database_items', category=cat['type'])
            li = xbmcgui.ListItem(cat['name'])
            li.setArt({'icon': 'DefaultFolder.png'})
            xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_database_items(category):
    """Lista itens de uma categoria da base de dados"""
    content = get_database_content()
    items = content.get(category, [])
    
    for item in items:
        magnet_url = f"plugin://plugin.video.elementum/play?uri={urllib.parse.quote(item['magnet'])}"
        
        display_name = item['title']
        if item.get('quality'):
            display_name += f" [{item['quality']}]"
        if item.get('audio'):
            display_name += f" ({item['audio']})"
        
        li = xbmcgui.ListItem(display_name)
        li.setProperty('IsPlayable', 'true')
        li.setInfo('video', {'title': item['title']})
        
        xbmcplugin.addDirectoryItem(addon_handle, magnet_url, li, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_database_search(query):
    """Pesquisa na base de dados"""
    content = get_database_content()
    results = []
    
    # Buscar em todas as categorias
    for category in ['movies', 'series', 'animes']:
        for item in content.get(category, []):
            if query.lower() in item['title'].lower():
                results.append(item)
    
    if not results:
        li = xbmcgui.ListItem("Nenhum resultado encontrado")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        for item in results:
            magnet_url = f"plugin://plugin.video.elementum/play?uri={urllib.parse.quote(item['magnet'])}"
            
            display_name = item['title']
            if item.get('quality'):
                display_name += f" [{item['quality']}]"
            if item.get('audio'):
                display_name += f" ({item['audio']})"
            
            li = xbmcgui.ListItem(display_name)
            li.setProperty('IsPlayable', 'true')
            li.setInfo('video', {'title': item['title']})
            
            xbmcplugin.addDirectoryItem(addon_handle, magnet_url, li, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def update_content():
    """Atualiza conteúdo"""
    xbmcgui.Dialog().notification('Cine Urso', 'Conteúdo atualizado!', xbmcgui.NOTIFICATION_INFO)
    list_main_categories()

def router():
    params = urllib.parse.parse_qs(sys.argv[2][1:])
    
    action = params.get('action', [''])[0]
    content_type = params.get('content_type', [''])[0]
    title = params.get('title', [''])[0]
    year = params.get('year', [''])[0]
    tmdb_id = params.get('tmdb_id', [''])[0]
    category = params.get('category', [''])[0]
    
    if not action:
        list_main_categories()
    elif action == 'list_tmdb':
        list_tmdb_content(content_type)
    elif action == 'list_torrent_sources':
        list_torrent_sources(title, year, content_type, tmdb_id)
    elif action == 'search_menu':
        search_menu()
    elif action == 'search':
        search_content(content_type)
    elif action == 'list_database':
        list_database()
    elif action == 'list_database_items':
        list_database_items(category)
    elif action == 'update_content':
        update_content()

if __name__ == '__main__':
    router()
