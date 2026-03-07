import subprocess
import platform
from PyQt6.QtCore import QThread, pyqtSignal
import time

class PingWorker(QThread):
    status_atualizado = pyqtSignal(str, bool)

    def __init__(self,hosts):
        super().__init__()
        self.hosts = hosts
        self.rodando = True

    def ping(self, host):
        sistema = platform.system().lower()
        
        if sistema == 'windows':
            comando = ['ping', '-n', '1', '-w', '1000', host]
        else:
            comando = ['ping', '-c', '1', '-W', '1', host]

        resultado = subprocess.run(
            comando,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return resultado.returncode == 0
    
    def run(self):
        while self.rodando:
            for host in self.hosts:
                online = self.ping(host)
                self.status_atualizado.emit(host, online)
            time.sleep(60)
    
    def stop(self):
        self.rodando = False