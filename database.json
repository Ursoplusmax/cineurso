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

# SUA URL DO GITHUB - TUDO VEM DAQUI!
DATABASE_URL = "https://raw.githubusercontent.com/Ursoplusmax/cineurso/main/database.json"

def get_url(**kwargs):
    return '{}?{}'.format(base_url, urllib.parse.urlencode(kwargs))

def get_content():
    '''Busca conteúdo do GitHub - ATUALIZAÇÃO AUTOMÁTICA!'''
    try:
        response = requests.get(DATABASE_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        xbmcgui.Dialog().notification('Erro', 'Verifique sua conexão', xbmcgui.NOTIFICATION_ERROR)
    
    return {"movies": [], "series": [], "animes": []}

def list_categories():
    '''Menu principal'''
    categories = [
        {'name': '🎬 FILMES', 'type': 'movies'},
        {'name': '📺 SÉRIES', 'type': 'series'}, 
        {'name': '🇯🇵 ANIMES', 'type': 'animes'},
        {'name': '🔄 ATUALIZAR CONTEÚDO', 'type': 'update'}
    ]
    
    for cat in categories:
        url = get_url(action='list_content', category=cat['type'])
        li = xbmcgui.ListItem(cat['name'])
        xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_content(category):
    '''Lista conteúdo - SEMPRE ATUALIZADO!'''
    if category == 'update':
        xbmcgui.Dialog().notification('Cine Urso', 'Conteúdo atualizado!', xbmcgui.NOTIFICATION_INFO)
        list_categories()
        return
        
    content = get_content()
    items = content.get(category, [])
    
    if not items:
        li = xbmcgui.ListItem("Nenhum conteúdo encontrado")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        for item in items:
            title = item['title']
            if 'quality' in item:
                title += f" [{item['quality']}]"
            if 'audio' in item:
                title += f" ({item['audio']})"
                
            # Elementum para streaming
            magnet_url = f"plugin://plugin.video.elementum/play?uri={urllib.parse.quote(item['magnet'])}"
            
            li = xbmcgui.ListItem(title)
            li.setProperty('IsPlayable', 'true')
            li.setInfo('video', {'title': item['title']})
            
            xbmcplugin.addDirectoryItem(addon_handle, magnet_url, li, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def router():
    params = urllib.parse.parse_qs(sys.argv[2][1:])
    
    if not params:
        list_categories()
    else:
        action = params.get('action', [''])[0]
        category = params.get('category', [''])[0]
        list_content(category)

if __name__ == '__main__':
    router()
