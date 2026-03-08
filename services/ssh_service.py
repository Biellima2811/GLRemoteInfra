import subprocess
import os
def abrir_ssh(host, usuario=None, porta=22):
    putty = os.path.join('assets', 'putty.exe')
    comando = [putty, '-ssh', host, '-P', str(porta)]

    if usuario:
        comando.extend(["-1", usuario])
    subprocess.Popen(comando)