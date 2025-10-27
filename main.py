# -*- coding: utf-8 -*-
import sys
import json
import urllib.parse
from urllib.parse import urlencode, quote_plus, parse_qsl, unquote_plus
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

HANDLE = int(sys.argv[1])
ADDON = xbmcaddon.Addon()

def router():
    params = dict(parse_qsl(sys.argv[2][1:]))
    action = params.get('action')

    if action is None:
        show_main_menu()
    elif action == 'search':
        search(query=params.get('query'))
    # ... outras ações serão adicionadas

def show_main_menu():
    xbmcplugin.setPluginCategory(HANDLE, 'Cine Urso')
    xbmcplugin.setContent(HANDLE, 'files')
    
    menus = [
        ('Pesquisar', 'search'),
        ('Filmes', 'movies_menu'),
        ('Séries', 'tvshows_menu'),
        ('Minha Lista', 'show_my_list'),
        ('Atualizar Banco', 'run_indexer')
    ]
    
    for title, action in menus:
        li = xbmcgui.ListItem(label=title)
        url = f"{sys.argv[0]}?action={action}"
        xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=True)
    
    xbmcplugin.endOfDirectory(HANDLE)

def search(query=None):
    if not query:
        keyboard = xbmc.Keyboard('', 'Pesquisar no Cine Urso')
        keyboard.doModal()
        if keyboard.isConfirmed():
            query = keyboard.getText()
    
    if query:
        xbmcgui.Dialog().notification("Cine Urso", f'Buscando: {query}')

if __name__ == '__main__':
    router()
