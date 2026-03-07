import os

# Biblioteca da interface
from PyQt6.QtWidgets import(
    QMainWindow,
    QTreeWidget,
    QTreeWidgetItem,
    QTabWidget,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel
)
from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMenu
from PyQt6.QtWidgets import QLineEdit
# Interface
from ui.nova_conexao import NovaConexao

# Banco de dados
from database.db import conectar

# Servicos
from services.rdp_service import abrir_rdp

# Monitoramento
from monitoring.ping_worker import PingWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        base_dir = os.path.dirname(__file__)
        icon_path = os.path.join(base_dir, "..", "assets", "icons", "rdp.png")
        QIcon(icon_path)
        
        # Tamanho inicial da janela
        self.setWindowTitle('GLRemoteInfra')
        
        # Tamanho inicial da janela
        self.resize(900,600)

        # Cria menu superior
        self.inicializar_interface()
        # Cria menu superior
        self.criar_menu()

    def inicializar_interface(self):
        # Widget principal
        container = QWidget()
        # Layout horizontal
        layout_principal = QVBoxLayout()
        layout = QHBoxLayout()
        
        self.search = QLineEdit()
        self.search.setPlaceholderText('Pesquisar servidor...')
        self.search.textChanged.connect(self.filtrar_servidores)

        layout_principal.addWidget(self.search)
        layout_principal.addLayout(layout)


        # Árvore de servidores (lado esquerdo)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel('Conexões')

        # evento duplo clique
        self.tree.itemDoubleClicked.connect(self.abrir_sessao)

        # Área de sessões (lado direito)
        self.tabs = QTabWidget()

        # Adiciona widgets ao layout
        layout.addWidget(self.tree, 2)
        layout.addWidget(self.tabs, 5)
        
        # Adiciona widgets ao layout
        container.setLayout(layout_principal)

        # Define container como conteúdo da janela
        self.setCentralWidget(container)
        
        # Carrega conexões do banco
        self.carregar_servidores()

        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.menu_conexao)

        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.fechar_aba)
    
    def carregar_servidores(self):
        self.hosts = []
        # Inicia monitoramento (valida os servidores que estiverem online)
        self.iniciar_monitoramento()
        self.tree.clear()
        conn = conectar()
        cursor = conn.execute('select nome, host, protocolo, grupo from conexoes')
        grupos = {}

        for nome, host, protocolo, grupo in cursor:

            if not grupo:
                grupo = 'Sem Grupo'
            
            # Cria um grupo se não existir
            if grupo not in grupos:
                grupo_item = QTreeWidgetItem(self.tree)
                grupo_item.setText(0,grupo)

                grupos[grupo] = grupo_item
            grupo_item = grupos[grupo]
            servidor = QTreeWidgetItem(grupo_item)
            servidor.setText(0, f'{nome} ({host})')
            
            if protocolo == 'RDP':
                servidor.setIcon(
                    0,QIcon('assets/icons/rdp.png')
                )
            elif protocolo == 'SSH':
                servidor.setIcon(
                    0,QIcon('assets/icons/ssh.png')
                )
            self.hosts.append(host)

        # Expande a árvore
        self.tree.expandAll()

        

    def abrir_sessao(self, item):
        texto = item.text(0)

        if '(' in texto:
            nome = texto.split('(')[0].strip()
            conn = conectar()
            cursor = conn.execute("select host, porta, protocolo from conexoes where nome=?", (nome,))
            resultado = cursor.fetchone()
            conn.close()

            if resultado:
                host, porta, protocolo = resultado
                
                if protocolo == 'RDP':
                    self.criar_aba(nome, host)
                    abrir_rdp(host, porta)
    
    def criar_menu(self):
        menu = self.menuBar()

        arquivo = menu.addMenu('Arquivo')

        nova = arquivo.addAction('Nova conexão')

        nova.triggered.connect(self.nova_conexoes)
    def criar_aba(self, nome, host):
        # widget da sessão
        widget = QWidget()
        layout = QHBoxLayout()
        label = QLabel(f'Sessão aberta para {nome} ({host})')
        layout.addWidget(label)
        widget.setLayout(layout)

        # Adiciona aba
        self.tabs.addTab(widget, nome)
        # Seleciona aba
        self.tabs.setCurrentWidget(widget)
    
    def fechar_aba(self, index):
        self.tabs.removeTab(index)
        
    def nova_conexoes(self):
        tela = NovaConexao()
        if tela.exec():
            self.carregar_servidores()
    
    def menu_conexao(self, pos):
        item = self.tree.itemAt(pos)
        if item is None:
            return
        
        menu = QMenu()

        conectar = menu.addAction('Conectar')
        editar = menu.addAction('Editar')
        excluir = menu.addAction('Excluir')

        action = menu.exec(self.tree.viewport().mapToGlobal(pos))

        if action == conectar:
            self.abrir_sessao(item)
        elif action == editar:
            print('Editar conexão')
        elif action == excluir:
            print('Excluir conexão')
    
    def filtrar_servidores(self, texto):
        texto = texto.lower()

        root = self.tree.invisibleRootItem()

        for i in range(root.childCount()):
            grupo = root.child(i)

            for j in range(grupo.childCount()):
                servidor = grupo.child(j)
                nome = servidor.text(0).lower()
                if texto in nome:
                    servidor.setHidden(False)
                else:
                    servidor.setHidden(True)
    
    def atualizar_status(self, host, online):
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            grupo = root.child(i)
            for j in range(grupo.childCount()):
                servidor = grupo.child(j)
                texto = servidor.text(0)

                if host in texto:
                    if online:
                        servidor.setIcon(
                        0, QIcon("assets/icons/online.png")
                    )
                    else:
                        servidor.setIcon(
                        0, QIcon("assets/icons/offline.png")
                    )

    def iniciar_monitoramento(self):
        self.worker = PingWorker(self.hosts)
        self.worker.status_atualizado.connect(self.atualizar_status)
        self.worker.start()