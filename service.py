import xbmc
import xbmcaddon
import os
import time

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
db_path = "D:\\MediaCenter\\Data\\media.db"

class MediaCenterService:
    def __init__(self):
        self.monitor = xbmc.Monitor()
    
    def check_database(self):
        """Verifica se o database existe e está acessível"""
        return os.path.exists(db_path)
    
    def run(self):
        """Loop principal do serviço"""
        xbmc.log(f"{addon_id} - Serviço iniciado", xbmc.LOGINFO)
        
        # Verificação inicial
        if not self.check_database():
            xbmc.log(f"{addon_id} - Database não encontrado: {db_path}", xbmc.LOGWARNING)
        
        # Loop principal
        while not self.monitor.abortRequested():
            # Verificar a cada 10 minutos
            if self.monitor.waitForAbort(600):
                break
            
            # Verificar database periodicamente
            if not self.check_database():
                xbmc.log(f"{addon_id} - Database ainda não disponível", xbmc.LOGDEBUG)
        
        xbmc.log(f"{addon_id} - Serviço finalizado", xbmc.LOGINFO)

if __name__ == '__main__':
    service = MediaCenterService()
    service.run()
