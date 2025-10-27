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
SENHA_ACESSO = "0404"  # 👈 Senha para entrar
DATABASE_URL = "https://raw.githubusercontent.com/Ursoplusmax/cineurso/main/database.json"

def get_url(**kwargs):
    return '{}?{}'.format(base_url, urllib.parse.urlencode(kwargs))

def verificar_senha():
    """Verifica senha de acesso"""
    keyboard = xbmc.Keyboard('', 'Digite a senha de acesso:')
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        senha_digitada = keyboard.getText()
        if senha_digitada == SENHA_ACESSO:
            return True
        else:
            xbmcgui.Dialog().ok('Acesso Negado', 'Senha incorreta!')
            return False
    return False

def get_database_content():
    """Busca da sua base de dados"""
    try:
        response = requests.get(DATABASE_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"categorias": {}}

def list_main_menu():
    """Menu principal após senha"""
    if not verificar_senha():
        return
    
    categories = [
        {'name': '🎬 FILMES', 'type': 'filmes', 'icon': 'DefaultMovies.png'},
        {'name': '📺 SÉRIES', 'type': 'series', 'icon': 'DefaultTVShows.png'},
        {'name': '🐉 ANIMES', 'type': 'animes', 'icon': 'DefaultGenre.png'},
        {'name': '🔍 PESQUISAR', 'type': 'search', 'icon': 'DefaultFolder.png'},
        {'name': '🔄 ATUALIZAR CONTEÚDO', 'type': 'update', 'icon': 'DefaultSettings.png'}
    ]
    
    for cat in categories:
        if cat['type'] in ['filmes', 'series', 'animes']:
            url = get_url(action='list_subcategories', category_type=cat['type'])
        elif cat['type'] == 'search':
            url = get_url(action='search_menu')
        else:
            url = get_url(action='update_content')
        
        li = xbmcgui.ListItem(cat['name'])
        li.setArt({'icon': cat['icon']})
        xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_subcategories(category_type):
    """Lista subcategorias"""
    content = get_database_content()
    categorias = content.get('categorias', {}).get(category_type, {})
    
    # Subcategorias padrão
    subcats_map = {
        'filmes': ['📁 RECENTES', '⭐ COLEÇÃO', '🔥 POPULARES', '🎭 GÊNEROS'],
        'series': ['📁 RECENTES', '⭐ COLEÇÃO', '📺 POR TEMPORADA'],
        'animes': ['📁 RECENTES', '⭐ COLEÇÃO', '🐉 SHONEN']
    }
    
    subcats = subcats_map.get(category_type, [])
    
    for subcat in subcats:
        # Verificar se tem conteúdo nesta subcategoria
        items = categorias.get(subcat, [])
        count = len(items) if items else 0
        
        url = get_url(action='list_content', category_type=category_type, subcategory=subcat)
        display_name = f"{subcat} ({count})" if count > 0 else subcat
        
        li = xbmcgui.ListItem(display_name)
        
        # Ícones para subcategorias
        icon_map = {
            '📁 RECENTES': 'DefaultRecentlyAdded.png',
            '⭐ COLEÇÃO': 'DefaultFavourites.png',
            '🔥 POPULARES': 'DefaultRating.png',
            '🎭 GÊNEROS': 'DefaultGenre.png',
            '📺 POR TEMPORADA': 'DefaultTV.png',
            '🐉 SHONEN': 'DefaultGenre.png'
        }
        
        li.setArt({'icon': icon_map.get(subcat, 'DefaultFolder.png')})
        xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_content(category_type, subcategory):
    """Lista conteúdos de uma subcategoria"""
    content = get_database_content()
    items = content.get('categorias', {}).get(category_type, {}).get(subcategory, [])
    
    if not items:
        li = xbmcgui.ListItem("Nenhum conteúdo encontrado")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        for item in items:
            # SEMPRE criar opção para ver fontes torrent
            url = get_url(
                action='list_torrent_sources', 
                title=item['title'],
                category_type=category_type,
                subcategory=subcategory
            )
            
            display_name = item['title']
            if item.get('quality'):
                display_name += f" [{item['quality']}]"
            if item.get('audio'):
                display_name += f" ({item['audio']})"
            
            li = xbmcgui.ListItem(display_name)
            li.setInfo('video', {
                'title': item['title'],
                'year': item.get('year'),
                'genre': ', '.join(item.get('genre', [])),
                'plot': item.get('description', '')
            })
            
            xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def list_torrent_sources(title, category_type, subcategory):
    """Lista fontes torrent para um conteúdo"""
    content = get_database_content()
    
    # Buscar o item específico
    items = content.get('categorias', {}).get(category_type, {}).get(subcategory, [])
    target_item = None
    
    for item in items:
        if item['title'] == title:
            target_item = item
            break
    
    if not target_item:
        li = xbmcgui.ListItem("Conteúdo não encontrado")
        xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    else:
        # Mostrar opções de torrent
        if target_item.get('magnet'):
            # Tem magnet único
            magnet_url = f"plugin://plugin.video.elementum/play?uri={urllib.parse.quote(target_item['magnet'])}"
            
            display_name = f"▶ {target_item['title']}"
            if target_item.get('quality'):
                display_name += f" [{target_item['quality']}]"
            if target_item.get('audio'):
                display_name += f" ({target_item['audio']})"
            if target_item.get('size'):
                display_name += f" - {target_item['size']}"
            
            li = xbmcgui.ListItem(display_name)
            li.setProperty('IsPlayable', 'true')
            li.setInfo('video', {'title': target_item['title']})
            
            xbmcplugin.addDirectoryItem(addon_handle, magnet_url, li, False)
        
        elif target_item.get('torrents'):
            # Tem múltiplos torrents
            for torrent in target_item['torrents']:
                magnet_url = f"plugin://plugin.video.elementum/play?uri={urllib.parse.quote(torrent['magnet'])}"
                
                display_name = f"▶ {torrent.get('quality', '')} - {torrent.get('audio', '')}"
                if torrent.get('size'):
                    display_name += f" - {torrent['size']}"
                
                li = xbmcgui.ListItem(display_name)
                li.setProperty('IsPlayable', 'true')
                li.setInfo('video', {'title': target_item['title']})
                
                xbmcplugin.addDirectoryItem(addon_handle, magnet_url, li, False)
        
        else:
            li = xbmcgui.ListItem("❌ Nenhum link torrent disponível")
            xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def search_menu():
    """Menu de pesquisa"""
    categories = [
        {'name': '🔍 PESQUISAR FILMES', 'type': 'filmes'},
        {'name': '🔍 PESQUISAR SÉRIES', 'type': 'series'},
        {'name': '🔍 PESQUISAR ANIMES', 'type': 'animes'}
    ]
    
    for cat in categories:
        url = get_url(action='search_content', category_type=cat['type'])
        li = xbmcgui.ListItem(cat['name'])
        li.setArt({'icon': 'DefaultFolder.png'})
        xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def search_content(category_type):
    """Pesquisa conteúdo"""
    keyboard = xbmc.Keyboard('', f'Pesquisar {category_type}:')
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        query = keyboard.getText()
        if query:
            content = get_database_content()
            all_items = []
            
            # Buscar em todas as subcategorias
            categorias = content.get('categorias', {}).get(category_type, {})
            for subcat, items in categorias.items():
                for item in items:
                    if query.lower() in item['title'].lower():
                        item['_subcategory'] = subcat  # Marcar de qual subcategoria veio
                        all_items.append(item)
            
            if not all_items:
                li = xbmcgui.ListItem("Nenhum resultado encontrado")
                xbmcplugin.addDirectoryItem(addon_handle, "", li, False)
            else:
                for item in all_items:
                    url = get_url(
                        action='list_torrent_sources', 
                        title=item['title'],
                        category_type=category_type,
                        subcategory=item['_subcategory']
                    )
                    
                    display_name = f"🔍 {item['title']}"
                    if item.get('quality'):
                        display_name += f" [{item['quality']}]"
                    if item.get('audio'):
                        display_name += f" ({item['audio']})"
                    
                    li = xbmcgui.ListItem(display_name)
                    li.setInfo('video', {'title': item['title']})
                    
                    xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
            
            xbmcplugin.endOfDirectory(addon_handle)

def update_content():
    """Atualiza conteúdo"""
    xbmcgui.Dialog().notification('Cine Urso', 'Conteúdo atualizado do GitHub!', xbmcgui.NOTIFICATION_INFO)
    list_main_menu()

def router():
    params = urllib.parse.parse_qs(sys.argv[2][1:])
    
    action = params.get('action', [''])[0]
    category_type = params.get('category_type', [''])[0]
    subcategory = params.get('subcategory', [''])[0]
    title = params.get('title', [''])[0]
    
    if not action:
        list_main_menu()
    elif action == 'list_subcategories':
        list_subcategories(category_type)
    elif action == 'list_content':
        list_content(category_type, subcategory)
    elif action == 'list_torrent_sources':
        list_torrent_sources(title, category_type, subcategory)
    elif action == 'search_menu':
        search_menu()
    elif action == 'search_content':
        search_content(category_type)
    elif action == 'update_content':
        update_content()

if __name__ == '__main__':
    router()
