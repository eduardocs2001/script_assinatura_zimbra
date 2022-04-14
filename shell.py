from banco_dados import base_sql
import os
import csv




#abre seção no shell
class connectio_shell:

    def __init__(self):
        pass

    def conect(self, cmd):
        shellcmd = os.popen(cmd)
        return shellcmd.read()

    def salve_connection(self, cmd, nome_arquivo):
        output = self.conect(cmd)
        with open(f"{nome_arquivo}.csv", "w") as out_file:
            for line in output:
                out_file.write(line)


class exec_shell:

    def __init__(self):
        self._conecta = connectio_shell()
        #puxa as contas do zimbra
        self._conecta.salve_connection('zmprov -l gaa', 'usuarios') 
        self._script_bd = base_sql()
        self._email = ''
        self._lista = []



    def dados(self):
        info = {}
        #campos que desejo puxar do zimbra 
        elementos = ['company', 'displayName', 'givenName', 'telephoneNumber', 'title' ]
        with open('info.csv', 'r') as file:
                    reader = csv.reader(file, delimiter = ':')
                    for row in reader:
                        info[row[0]] = row[1]
        lista = []
        #se o campo que chamei estiver vazio, ele substituira por um espaço
        for x in elementos:
            try:
                lista.append(info[x])
            except:
                lista.append(' ')

        return lista


    def processa_shell_novos(self):
        dados = []
        with open('usuarios.csv', 'r') as file:
            reader = csv.reader(file, delimiter = ':')
            for row in reader:
                dados.append(row[0]) #puxa os email das contas do zimbra
        dados_bd = list(map(lambda x: x[0],self._script_bd.read('email'))) #puxa email do banco de dados.
        for email in dados:
            self._email = email
            if email not in dados_bd: #se o email que está no zimbra não existe no banco de dados execute:
                #solicita os dados dos campos do email
                #para puxar outros campos, apenas acesse a configuração da conta, e de dois click sobre o campo desejado
                self._conecta.salve_connection(f"zmprov ga {email}  | grep '^givenName\|^displayName\|^company\|^description\|^telephoneNumber\|^title'", 'info')#extrai as informação
                self._lista = self.dados()
                self._lista
                self._script_bd.inserir(self._lista[1], email, self._lista[4], self._lista[0], self._lista[3])
                """
                se você estiver executando pela primeira vez em um servidor zimbra onde já existe contas com assinaturas,
                e você não deseja atualizar, comente as duas funçoes abaixo"""
                self.nova_assinatura()
                self.envia_template()
            else:
                pass #já existe




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
        #verifica se o contato já tem uma assinatura existente
        id = self._conecta.conect(f'zmprov getSignatures {self._email} | grep zimbraSignatureId')
        if len(id) > 0:
            #se tiver existente, apenas atualiza
            coman = f"""zmprov ma {self._email} zimbraPrefMailSignatureHTML '{self.nova_assinatura()}'"""
            self._conecta.conect(coman)
        else:
            #se não existir, cria
            comand = f"""zmprov ma {self._email} zimbraSignatureName 'Padrao'; zmprov ma {self._email} zimbraPrefMailSignatureHTML '{self.nova_assinatura()}'"""
            self._conecta.conect(comand)


a = exec_shell()
a.processa_shell_novos()
