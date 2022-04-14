from banco_dados import base_sql
from paramiko import SSHClient, AutoAddPolicy
import csv
import os
import time

class connection_ssh:

    def __init__(self, ssh_user, ssh_password, ssh_host, ssh_port):
        self.SSH_USER = ssh_user
        self.SSH_PASSWORD = ssh_password
        self.SSH_HOST = ssh_host
        self.SSH_PORT = ssh_port
        self.client = SSHClient()
        self.conect()
    
    #abre a conexão
    def conect(self):
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        try:
            self.client.connect(self.SSH_HOST, port=self.SSH_PORT,
                                    username=self.SSH_USER,
                                    password=self.SSH_PASSWORD,
                                    look_for_keys=False)
            print('Conexão aberta')
        except Exception:
            print("Failed to establish connection_ssh.")

    """
     STDOUT = saída
     STDERR = retorna erros
     STDIN = envia texto de volta ao comando executado
    """
    #faz a requisição via ssh e salva a saída dentro de um arquivo csv
    def comando(self, cmd, nome_arquivo):
        cmdo = cmd
        stdin, stdout, stderr = self.client.exec_command(cmdo) 
        output = stdout.readlines()
        #salva saída em um arquivo externo
        with open(f"{nome_arquivo}.csv", "w") as out_file:
            for line in output:
                out_file.write(line)
    #faz a requisição ssh e retorna a saida no terminal

    def envia(self, cmd):
        cmdo = cmd
        stdin, stdout, stderr = self.client.exec_command(cmdo) 
        saida = stdout.readlines()
        return saida

class exec_ssh:

    def __init__(self):
        self.ssh = connection_ssh('usuario', 'senha', 'ip', 'porta')
        self.ssh.comando('zmprov -l gaa', 'usuarios') #puxa os email
        self.emails = 'usuarios.csv'
        self.info = 'info.csv'
        self.id = 'id.csv'
        self.script_bd = base_sql()
        self.lista = []
        self.email = ''
        
    def dados(self):
        info = {}
        elementos = ['company', 'displayName', 'givenName', 'telephoneNumber', 'title' ]
        with open('info.csv', 'r') as file:
                    reader = csv.reader(file, delimiter = ':')
                    for row in reader:
                        info[row[0]] = row[1]
        lista = []
        for x in elementos:
            try:
                lista.append(info[x])
            except:
                lista.append(' ')
        
        return lista

    def processa_ssh_novos(self):
        dados = []
        with open('usuarios.csv', 'r') as file:
            reader = csv.reader(file, delimiter = ':')
            for row in reader:
                dados.append(row[0]) #puxa os email  
        dados_bd = list(map(lambda x: x[0],self.script_bd.read('email'))) #puxa email do banco de dados
        for email in dados:
            print('Executando....\n')
            self.email = email
            try:
                if email not in dados_bd: #não existe
                    self.ssh.comando(f"zmprov ga {email}  | grep '^givenName\|^displayName\|^company\|^description\|^telephoneNumber\|^title'", 'info')#extrai as informação
                    self.lista = self.dados()
                    self.script_bd.inserir(self.lista[1], email, self.lista[4], self.lista[0], self.lista[3])
                    self.nova_assinatura()
                    self.envia_template()
                else:
                    pass #já existe
            except:
                pass

    def nova_assinatura(self):
        #exemplo de template 
        #para saber a posição de cada item, de um print no self._lista
        template = f'''<div>
        <table style="font-size:13.3333px">
                <tbody style="font-family: trebuchet ms, sans-serif; font-size: 10pt;">
                        <tr style="color: #808080">
                        <td style="color: #339966"> <span> Classifica&ccedil;&atilde;o da Informa&ccedil;&atilde;o: </span> </td>
                        <td><pre> (  ) Confidencial</pre></td>
                        <td><pre> ( X ) Interna</pre></td>
                        <td><pre> (  ) P&uacute;blica</pre></td>
                        </tr>
                </tbody>
        </table>
        <hr style="font-size: 13.3333px;" />
        <p style="margin: 0cm 0cm 0.0001pt 8.8pt; font-size: 10pt; font-family: Trebuchet MS, sans-serif;">
                <span style="color: #7f7f7f; ">Atenciosamente</span><br>
                <span style="color: #007244; "><strong>{self._lista[1]} -> nome</strong></span><br>
                <span style="color: #7f7f7f; ">{self._lista[4]} -> Profissão</span><br>
                <span style="color: #7f7f7f; ">Nome da empresa</span><br>
                <span style="color: #007244; ">telefone: {self._lista[3]}-> contato  | e-mail: {self._email}->email  </span><br>
                <span style="color: #7f7f7f; ">site da empresa | WhatsApp <span style="color: #007244"> whats da empresa </span> | SAC <span style="color: #007244"> 0800 645 0221 </span> | Transporte <span style="color: #007244"> 0800 0488 488 </span> </span><br><br>
                <img src="logo da empresa" />
        </p>
        </div>'''
        return template
        
    def envia_template(self):
        id = self.ssh.envia(f'zmprov getSignatures {self.email} | grep zimbraSignatureId')
        if len(id) > 0:
            coman = f"""zmprov ma {self.email} zimbraPrefMailSignatureHTML '{self.nova_assinatura()}'"""
            self.ssh.envia(coman)
        else:
            comand = f"""zmprov ma {self.email} zimbraSignatureName 'Padrao'; zmprov ma {self.email} zimbraPrefMailSignatureHTML '{self.nova_assinatura()}'"""
            self.ssh.envia(comand)

b = exec_ssh()
b.processa_ssh_novos()