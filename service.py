import xbmc
import xbmcaddon
import time

ADDON = xbmcaddon.Addon()
MONITOR = xbmc.Monitor()

def log(msg):
    xbmc.log(f"[Cine Urso Service] {msg}", level=xbmc.LOGINFO)

if __name__ == '__main__':
    log('Serviço do Cine Urso iniciado.')
    
    while not MONITOR.abortRequested():
        # Verificar atualizações a cada 30 minutos
        log('Verificando atualizações...')
        
        # Aguardar 30 minutos ou até abortar
        if MONITOR.waitForAbort(1800):
            break

    log('Serviço do Cine Urso finalizado.')
