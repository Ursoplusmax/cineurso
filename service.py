# D:\MediaCenter\Kodi\Addon\service.py
import xbmc
import xbmcaddon
import os
import json

addon = xbmcaddon.Addon()
db_path = "D:\\MediaCenter\\Data\\media.db"

class MediaCenterService:
    def __init__(self):
        self.monitor = xbmc.Monitor()
    
    def check_database(self):
        """Verifica se o database existe"""
        return os.path.exists(db_path)
    
    def run(self):
        """Loop principal do serviço"""
        xbmc.log("Media Center Service started", xbmc.LOGINFO)
        
        while not self.monitor.abortRequested():
            # Verificar database a cada 30 segundos
            if self.monitor.waitForAbort(30):
                break
            
            if not self.check_database():
                xbmc.log("Media Center database not found", xbmc.LOGWARNING)
        
        xbmc.log("Media Center Service stopped", xbmc.LOGINFO)

if __name__ == '__main__':
    service = MediaCenterService()
    service.run()
