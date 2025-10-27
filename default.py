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

DATABASE_URL = "https://raw.githubusercontent.com/Ursoplusmax/cineurso/main/database.json"

def get_url(**kwargs):
    return '{}?{}'.format(base_url, urllib.parse.urlencode(kwargs))

def get_content():
    try:
        response = requests.get(DATABASE_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Erro: {e}")
    return {"categorias": {}}

def list_categories():
    '''Menu principal'''
    categories = [
        {'name': '🔍 PESQUISAR', 'type': 'search', 'icon': 'DefaultFolder.png'},
        {'name': '🎬 FILMES', 'type': 'filmes', 'icon': 'DefaultMovies.png'},
        {'name': '📺 SÉRIES', 'type': 'series', 'icon': 'DefaultTVShows.png'},
        {'name': '🐉 ANIMES', 'type': 'animes', 'icon': 'DefaultGenre.png'},
        {'name': '🔄 ATUALIZAR CONTEÚDO', 'type': 'update', 'icon': 'DefaultFolder.png'}
    ]
    
    for cat in categories:
        if cat['type'] == 'search':
            url = get_url(action='search')
        elif cat['type'] == 'update':
            url = get_url(action='update')
        else:
            url = get_url(action='list_subcategories', category_type=cat['type'])
        
        li = xbmcgui.ListItem(cat['name'])
        li.setArt({'icon': cat['icon']})
        xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_subcategories(category_type):
    '''Lista subcategorias de filmes, séries ou animes'''
    content = get_content()
    categorias = content.get('categorias', {}).get(category_type, {})
    
    # Subcategorias padrão para cada tipo
    default_subcats = {
        'filmes': [
            '📁 RECENTES', '⭐ COLEÇÃO', '🔥 POPULARES', 
            '🎭 GÊNEROS', '🎯 4K UHD', '📅 POR ANO'
        ],
        'series': [
            '📁 RECENTES', '⭐ COLEÇÃO', '🔥 POPULARES', 
            '🎭 GÊNEROS', '📅 POR ANO', '📺 POR TEMPORADA'
        ],
        'animes': [
            '📁 RECENTES', '⭐ COLEÇÃO', '🔥 POPULARES', 
            '🎭 GÊNEROS', '📅 POR ANO', '🐉 SHONEN'
        ]
    }
    
    subcats = default_subcats.get(category_type, [])
    
    for subcat in subcats:
        url = get_url(action='list_content', category_type=category_type, subcategory=subcat)
        li = xbmcgui.ListItem(subcat)
        
        # Ícones para subcategorias
        icon_map = {
            '📁 RECENTES': 'DefaultRecentlyAdded.png',
            '⭐ COLEÇÃO': 'DefaultFavourites.png',
            '🔥 POPULARES': 'DefaultRating.png',
            '🎭 GÊNEROS': 'DefaultGenre.png',
            '🎯 4K UHD': 'DefaultVideo.png',
            '📅 POR ANO': 'DefaultYear.png',
            '📺 POR TEMPORADA': 'DefaultTV.png',
            '🐉 SHONEN': 'DefaultGenre.png'
        }
        
        li.setArt({'icon': icon_map.get(subcat, 'DefaultFolder.png')})
        xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_content(category_type, subcategory):
    '''Lista conteúdos de uma subcategoria'''
    content = get_content()
    
    # Buscar conteúdos reais do JSON
    items = content.get('categorias', {}).get(category_type, {}).get(subcategory, [])
    
    if not items:
        # Conteúdo de exemplo se não encontrar
        items = get_sample_content(category_type, subcategory)
    
    for item in items:
        title = item['title']
        if 'quality' in item:
            title += f" [{item['quality']}]"
        if 'audio' in item:
            title += f" ({item['audio']})"
        if 'size' in item:
            title += f" - {item['size']}"
        
        magnet_url = f"plugin://plugin.video.elementum/play?uri={urllib.parse.quote(item['magnet'])}"
        
        li = xbmcgui.ListItem(title)
        li.setProperty('IsPlayable', 'true')
        li.setInfo('video', {
            'title': item['title'],
            'year': item.get('year'),
            'genre': ', '.join(item.get('genre', [])) if item.get('genre') else ''
        })
        
        xbmcplugin.addDirectoryItem(addon_handle, magnet_url, li, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def get_sample_content(category_type, subcategory):
    '''Conteúdo de exemplo para teste'''
    samples = {
        'filmes': {
            '📁 RECENTES': [
                {'title': 'Oppenheimer (2023)', 'magnet': 'magnet:?xt=urn:btih:1234567890ABCDEF', 'quality': '1080p', 'audio': 'Legendado', 'size': '4.2 GB', 'year': 2023, 'genre': ['Drama', 'Histórico']},
                {'title': 'Barbie (2023)', 'magnet': 'magnet:?xt=urn:btih:2234567890ABCDEF', 'quality': '1080p', 'audio': 'Dublado', 'size': '3.8 GB', 'year': 2023, 'genre': ['Comédia', 'Fantasia']}
            ],
            '⭐ COLEÇÃO': [
                {'title': 'Trilogia Senhor dos Anéis', 'magnet': 'magnet:?xt=urn:btih:3234567890ABCDEF', 'quality': '1080p', 'audio': 'Legendado', 'size': '25 GB', 'year': 2003, 'genre': ['Fantasia', 'Aventura']}
            ],
            '🎯 4K UHD': [
                {'title': 'Avatar: O Caminho da Água (2022) 4K', 'magnet': 'magnet:?xt=urn:btih:4234567890ABCDEF', 'quality': '4K', 'audio': 'Dublado', 'size': '18.5 GB', 'year': 2022, 'genre': ['Ficção', 'Aventura']}
            ]
        },
        'series': {
            '📁 RECENTES': [
                {'title': 'The Last of Us S01E01', 'magnet': 'magnet:?xt=urn:btih:5234567890ABCDEF', 'quality': '1080p', 'audio': 'Legendado', 'size': '2.8 GB', 'year': 2023, 'genre': ['Drama', 'Suspense']}
            ]
        },
        'animes': {
            '📁 RECENTES': [
                {'title': 'Attack on Titan Final', 'magnet': 'magnet:?xt=urn:btih:6234567890ABCDEF', 'quality': '1080p', 'audio': 'Japonês/Legendado', 'size': '1.8 GB', 'year': 2023, 'genre': ['Ação', 'Fantasia']}
            ],
            '🐉 SHONEN': [
                {'title': 'Demon Slayer: Vila dos Ferreiros', 'magnet': 'magnet:?xt=urn:btih:7234567890ABCDEF', 'quality': '1080p', 'audio': 'Japonês/Legendado', 'size': '1.5 GB', 'year': 2023, 'genre': ['Ação', 'Fantasia']}
            ]
        }
    }
    
    return samples.get(category_type, {}).get(subcategory, [])

def search_content():
    '''Função de pesquisa'''
    keyboard = xbmc.Keyboard('', 'Digite o nome do filme/série:')
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_term = keyboard.getText()
        if search_term:
            xbmcgui.Dialog().notification('Pesquisa', f'Buscando: {search_term}', xbmcgui.NOTIFICATION_INFO)

def update_content():
    '''Força atualização do conteúdo'''
    xbmcgui.Dialog().notification('Cine Urso', 'Conteúdo atualizado do GitHub!', xbmcgui.NOTIFICATION_INFO)
    list_categories()

def router():
    params = urllib.parse.parse_qs(sys.argv[2][1:])
    
    action = params.get('action', [''])[0]
    category_type = params.get('category_type', [''])[0]
    subcategory = params.get('subcategory', [''])[0]
    
    if not action:
        list_categories()
    elif action == 'list_subcategories':
        list_subcategories(category_type)
    elif action == 'list_content':
        list_content(category_type, subcategory)
    elif action == 'search':
        search_content()
    elif action == 'update':
        update_content()

if __name__ == '__main__':
    router()
