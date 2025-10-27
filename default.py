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

# SUA URL - JÁ FUNCIONANDO!
DATABASE_URL = "https://raw.githubusercontent.com/Ursoplusmax/cineurso/main/database.json"

def get_url(**kwargs):
    return '{}?{}'.format(base_url, urllib.parse.urlencode(kwargs))

def get_content():
    '''Busca conteúdo do GitHub'''
    try:
        response = requests.get(DATABASE_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Erro: {e}")
    
    return {"categorias": {}}

def list_main_menu():
    '''Menu principal com categorias'''
    menu_items = [
        {'name': '🎬 FILMES', 'type': 'filmes', 'icon': 'DefaultMovies.png'},
        {'name': '📺 SÉRIES', 'type': 'series', 'icon': 'DefaultTVShows.png'},
        {'name': '🇯🇵 ANIMES', 'type': 'animes', 'icon': 'DefaultGenre.png'},
        {'name': '🔄 ATUALIZAR', 'type': 'update', 'icon': 'DefaultFolder.png'}
    ]
    
    for item in menu_items:
        url = get_url(action='list_categories', category_type=item['type'])
        li = xbmcgui.ListItem(item['name'])
        li.setArt({'icon': item['icon']})
        xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_categories(category_type):
    '''Lista subcategorias (Ação, Comédia, Terror, etc)'''
    content = get_content()
    categorias = content.get('categorias', {}).get(category_type, {})
    
    if not categorias:
        li = xbmcgui.ListItem("Nenhuma categoria encontrada")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        # Ordenar categorias alfabeticamente
        for cat_name in sorted(categorias.keys()):
            item_count = len(categorias[cat_name])
            display_name = f"📂 {cat_name.upper()} ({item_count})"
            
            url = get_url(action='list_content', category_type=category_type, subcategory=cat_name)
            li = xbmcgui.ListItem(display_name)
            li.setArt({'icon': 'DefaultGenre.png'})
            xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_content(category_type, subcategory):
    '''Lista conteúdos de uma subcategoria'''
    content = get_content()
    items = content.get('categorias', {}).get(category_type, {}).get(subcategory, [])
    
    if not items:
        li = xbmcgui.ListItem("Nenhum conteúdo nesta categoria")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        for item in items:
            # Construir título informativo
            title = item['title']
            if 'quality' in item:
                title += f" [{item['quality']}]"
            if 'audio' in item:
                title += f" ({item['audio']})"
            if 'size' in item:
                title += f" - {item['size']}"
            
            # URL para Elementum
            magnet_url = f"plugin://plugin.video.elementum/play?uri={urllib.parse.quote(item['magnet'])}"
            
            li = xbmcgui.ListItem(title)
            li.setProperty('IsPlayable', 'true')
            li.setInfo('video', {
                'title': item['title'],
                'year': item.get('year'),
                'genre': item.get('genre', [''])[0] if item.get('genre') else ''
            })
            
            xbmcplugin.addDirectoryItem(addon_handle, magnet_url, li, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def update_content():
    '''Força atualização do conteúdo'''
    xbmcgui.Dialog().notification('Cine Urso', 'Conteúdo atualizado!', xbmcgui.NOTIFICATION_INFO)

def router():
    params = urllib.parse.parse_qs(sys.argv[2][1:])
    
    action = params.get('action', [''])[0]
    category_type = params.get('category_type', [''])[0]
    subcategory = params.get('subcategory', [''])[0]
    
    if not action:
        list_main_menu()
    elif action == 'list_categories':
        if category_type == 'update':
            update_content()
            list_main_menu()
        else:
            list_categories(category_type)
    elif action == 'list_content':
        list_content(category_type, subcategory)

if __name__ == '__main__':
    router()
