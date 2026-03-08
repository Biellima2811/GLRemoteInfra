from PyQt6.QtWidgets import(
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox
)

from database.db import conectar

class NovaConexao(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Nova Conexão')
        
        layout = QVBoxLayout()

        self.nome = QLineEdit()
        self.host = QLineEdit()
        self.usuario = QLineEdit()
        self.senha = QLineEdit()
        self.senha.setEchoMode(QLineEdit.echoMode.Password)
        self.porta = QLineEdit()
        self.grupo = QLineEdit()
        
        self.protocolo = QComboBox()
        self.protocolo.addItems(['RDP', 'SSH'])

        salvar = QPushButton('Salvar')
        salvar.clicked.connect(self.salvar)

        layout.addWidget(QLabel('Nome'))
        layout.addWidget(self.nome)

        layout.addWidget(QLabel('IP'))
        layout.addWidget(self.host)

        layout.addWidget(QLabel('Usuário'))
        layout.addWidget(self.usuario)

        layout.addWidget(QLabel('Senha'))
        layout.addWidget(self.senha)

        layout.addWidget(QLabel('Porta'))
        layout.addWidget(self.porta)


        layout.addWidget(QLabel('Protocolo'))
        layout.addWidget(self.protocolo)

        layout.addWidget(QLabel('Grupo'))
        layout.addWidget(self.grupo)

        layout.addWidget(salvar)
        self.setLayout(layout)

    def salvar(self):
        conn = conectar()

        conn.execute("""
            INSERT INTO conexoes
            (nome,host,usuario,senha,porta,protocolo,grupo)
            VALUES (?,?,?,?,?,?,?)
            """,(
            self.nome.text(),
            self.host.text(),
            self.usuario.text(),
            self.senha.text(),
            self.porta.text(),
            self.protocolo.currentText(),
            self.grupo.text()
            ))
        conn.commit()
        self.accept()