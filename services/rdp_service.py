import subprocess

def abrir_rdp(host, porta=None):
    if porta:
        endereco = f'{host}:{porta}'
    else:
        endereco = host
    
    comando = ['mstsc', f'/v:{endereco}']
    subprocess.Popen(comando)
    