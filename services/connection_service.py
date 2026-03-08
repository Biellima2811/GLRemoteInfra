from database.db import conectar

class ConnectionService:
    def listar_conexoes(self):
        conn = conectar()
        cursor = conn.execute(
            "select nome, host, protocolo, grupo from conexoes"
        )

        dados = cursor.fetchall()
        conn.close()
        return dados
    
    def buscar_por_nome(self, nome):
        conn = conectar()

        cursor = conn.execute(
            "select host, porta, protocolo from conexoes where nome=?", (nome,)
        )
        resultado = cursor.fetchone()

        conn.close()
        return resultado
    
    def excluir_conexao(self, nome):
        conn = conectar()

        conn.execute("delete from conexoes where nome=?", (nome,))
        conn.commit()
        conn.close()