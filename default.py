def update_library():
    """Update media library - VERSÃO CORRIGIDA"""
    try:
        import subprocess
        import os
        
        # Caminho do script PowerShell
        script_path = "D:\\MediaCenter\\Scripts\\MediaCenterAddon.ps1"
        
        if os.path.exists(script_path):
            # Comando PowerShell corrigido
            command = [
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-File", script_path,
                "scan"
            ]
            
            # Executar em background sem esperar
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE - esconder janela
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo
            )
            
            show_notification("Scan iniciado... Pode demorar alguns minutos.")
            
        else:
            show_notification("Script do Media Center não encontrado!")
            log(f"Script path not found: {script_path}", xbmc.LOGERROR)
            
    except Exception as e:
        log(f"Erro no update: {str(e)}", xbmc.LOGERROR)
        show_notification("Erro ao iniciar scan!")
