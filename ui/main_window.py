import os

from PyQt6.QtWidgets import (
    QMainWindow,
    QTreeWidget,
    QTreeWidgetItem,
    QTabWidget,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QMenu,
    QLineEdit
)

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Interface
from ui.nova_conexao import NovaConexao

# Services
from services.rdp_service import abrir_rdp
from services.ssh_service import abrir_ssh
from services.connection_service import ConnectionService

# Monitoramento
from monitoring.ping_worker import PingWorker


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GLRemoteInfra")
        self.resize(900, 600)

        self.connection_service = ConnectionService()

        self.inicializar_interface()
        self.criar_menu()

    def inicializar_interface(self):

        container = QWidget()

        layout_principal = QVBoxLayout()
        layout = QHBoxLayout()

        # Campo busca
        self.search = QLineEdit()
        self.search.setPlaceholderText("Pesquisar servidor...")
        self.search.textChanged.connect(self.filtrar_servidores)

        layout_principal.addWidget(self.search)
        layout_principal.addLayout(layout)

        # Árvore
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Conexões")
        self.tree.itemDoubleClicked.connect(self.abrir_sessao)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.fechar_aba)

        layout.addWidget(self.tree, 2)
        layout.addWidget(self.tabs, 5)

        container.setLayout(layout_principal)

        self.setCentralWidget(container)

        # Menu contexto
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.menu_conexao)

        self.carregar_servidores()

    def criar_menu(self):

        menu = self.menuBar()

        arquivo = menu.addMenu("Arquivo")

        nova = arquivo.addAction("Nova conexão")

        nova.triggered.connect(self.nova_conexoes)

    def carregar_servidores(self):

        self.tree.clear()

        self.hosts = []

        conexoes = self.connection_service.listar_conexoes()

        grupos = {}

        for nome, host, protocolo, grupo in conexoes:

            if not grupo:
                grupo = "Sem Grupo"

            if grupo not in grupos:
                grupo_item = QTreeWidgetItem(self.tree)
                grupo_item.setText(0, grupo)

                grupos[grupo] = grupo_item

            grupo_item = grupos[grupo]

            servidor = QTreeWidgetItem(grupo_item)
            servidor.setText(0, nome)
            servidor.setData(
                {
                    'nome':nome,
                    'host':host,
                    'protocolo':protocolo
                }
            )

            if protocolo == "RDP":
                servidor.setIcon(0, QIcon("assets/icons/rdp.png"))

            elif protocolo == "SSH":
                servidor.setIcon(0, QIcon("assets/icons/ssh.png"))

            self.hosts.append(host)

        self.tree.expandAll()

        self.iniciar_monitoramento()

    def abrir_sessao(self, item):
        dados = item.data(0,Qt.ItemDataRole.UserRole)
        
        nome = dados['nome']
        host = dados['host']
        protocolo = dados['protocolo']

        resultado = self.connection_service.buscar_por_nome(nome)

        if not resultado:
            return

        host, porta, protocolo = resultado

        if protocolo == "RDP":

            self.criar_aba(nome, host)

            abrir_rdp(host, porta)

        elif protocolo == "SSH":

            abrir_ssh(host)

    def criar_aba(self, nome, host):

        widget = QWidget()

        layout = QHBoxLayout()

        label = QLabel(f"Sessão aberta para {nome} ({host})")

        layout.addWidget(label)

        widget.setLayout(layout)

        self.tabs.addTab(widget, nome)

        self.tabs.setCurrentWidget(widget)

    def fechar_aba(self, index):

        self.tabs.removeTab(index)

    def nova_conexoes(self):

        tela = NovaConexao()
        self.statusBar().showMessage('GLRemoteInfra iniciado')

        if tela.exec():

            self.carregar_servidores()

    def menu_conexao(self, pos):

        item = self.tree.itemAt(pos)

        if item is None:
            return

        menu = QMenu()

        conectar = menu.addAction("Conectar")
        editar = menu.addAction("Editar")
        excluir = menu.addAction("Excluir")

        action = menu.exec(self.tree.viewport().mapToGlobal(pos))

        if action == conectar:

            self.abrir_sessao(item)

        elif action == editar:

            print("Editar conexão")

        elif action == excluir:
            dados = item.data(0, Qt.ItemDataRole.UserRole)
            nome = dados['nome']
            self.connection_service.excluir_conexao(nome)
            self.carregar_servidores

    def filtrar_servidores(self, texto):

        texto = texto.lower()

        root = self.tree.invisibleRootItem()

        for i in range(root.childCount()):

            grupo = root.child(i)

            for j in range(grupo.childCount()):

                servidor = grupo.child(j)

                nome = servidor.text(0).lower()

                servidor.setHidden(texto not in nome)

    def atualizar_status(self, host, online):

        root = self.tree.invisibleRootItem()

        for i in range(root.childCount()):

            grupo = root.child(i)

            for j in range(grupo.childCount()):

                servidor = grupo.child(j)

                texto = servidor.text(0)

                if host in texto:

                    if online:

                        servidor.setIcon(0, QIcon("assets/icons/online.png"))

                    else:

                        servidor.setIcon(0, QIcon("assets/icons/offline.png"))

    def iniciar_monitoramento(self):
        if not self.hosts:
            return
        self.worker = PingWorker(self.hosts)
        self.worker.status_atualizado.connect(self.atualizar_status)
        self.worker.start()