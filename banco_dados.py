import sqlite3
import io

class base_sql:

    def __init__(self):
        self.__conecta = sqlite3.connect('Nome_do_banco_dados.db')
        self.__cursor = self.__conecta.cursor()


    def schema(self):
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                profissao TEXT NOT NULL,
                empresa TEXT NOT NULL,
                contato TEXT NOT NULL);
                """)

    def inserir(self, nome, email, profissao, empresa, contato):
        lista = [nome, email, profissao, empresa, contato]
        self.__cursor.execute("INSERT INTO usuarios (nome, email, profissao, empresa, contato) VALUES (?,?,?, ?, ?)", lista)
        self.__conecta.commit()


    def read(self, campo):
        info = self.__cursor.execute(f'SELECT {campo} FROM usuarios').fetchall()
        return info

    def update(self, dados):
        lista = [dados["nome_novo"], dados["email_novo"], dados["profissao_novo"], dados["empresa_novo"], dados['contato_novo'], dados["email_antigo"]]
        self.__cursor.execute(
        """UPDATE usuarios SET nome = ?, email = ?, profissao = ?, empresa = ?, contato = ?
        WHERE email = ?
        """, lista)
        self.__conecta.commit()


    def delete(self, email):
        self.__cursor.execute(f"DELETE FROM usuarios WHERE email = ?",email)
        self.__conecta.commit()


    def backup(self):
        with io.open('cliente_dump.sql', 'w') as f:
            for linha in self._conecta.iterdump():
                f.write('%s\n' % linha)