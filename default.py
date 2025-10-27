# D:\MediaCenter\Kodi\default.py
import os
import json
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')
db_path = "D:\\MediaCenter\\Data\\media.db"

def load_media_data():
    """Carrega dados do banco do Media Center"""
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def list_categories():
    """Lista categorias principais"""
    categories = [
        ('Filmes', 'movies'),
        ('Séries', 'series'),
        ('Animes', 'animes'),
        ('Biblioteca Completa', 'all')
    ]
    
    for name, category in categories:
        li = xbmcgui.ListItem(name)
        url = f'{addon_url}?action=list&category={category}'
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_media(category):
    """Lista mídia por categoria"""
    data = load_media_data()
    
    if category == 'movies':
        items = [item for item in data if item.get('Type') == 'Filme']
    elif category == 'series':
        items = [item for item in data if item.get('Type') == 'Série']
    elif category == 'animes':
        items = [item for item in data if item.get('Type') == 'Anime']
    else:
        items = data
    
    for item in items:
        title = item.get('Name') or f"{item.get('Series', item.get('Anime'))} - {item.get('Episode')}"
        path = item.get('Path', '')
        
        li = xbmcgui.ListItem(title)
        li.setInfo('video', {'title': title})
        li.setProperty('IsPlayable', 'true')
        
        xbmcplugin.addDirectoryItem(
            handle=addon_handle, 
            url=path, 
            listitem=li, 
            isFolder=False
        )
    
    xbmcplugin.endOfDirectory(addon_handle)

def main():
    args = xbmcplugin.getAddonInfo('path')
    params = dict(arg.split('=') for arg in args.split('&') if '=' in arg)
    
    action = params.get('action', 'main')
    category = params.get('category', '')
    
    if action == 'list':
        list_media(category)
    else:
        list_categories()

if __name__ == '__main__':
    main()
