import xbmc
import xbmcaddon
import os

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
db_path = "D:\\MediaCenter\\Data\\media.db"

class MediaCenterService:
    def __init__(self):
        self.monitor = xbmc.Monitor()
    
    def check_database(self):
        return os.path.exists(db_path)
    
    def run(self):
        xbmc.log(f"{addon_id} service started", xbmc.LOGINFO)
        
        while not self.monitor.abortRequested():
            # Verificar database a cada 5 minutos
            if self.monitor.waitForAbort(300):
                break
            
            if not self.check_database():
                xbmc.log(f"{addon_id} - Database not found", xbmc.LOGWARNING)
        
        xbmc.log(f"{addon_id} service stopped", xbmc.LOGINFO)

if __name__ == '__main__':
    service = MediaCenterService()
    service.run()
