# Importa bibliotecas necessárias
import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import mysql.connector

# Define a classe principal do jogo
class JogoPerguntasRespostas(tk.Tk):

    #Index de cada Tupla para localizar no banco
    PERGUNTA_INDEX = 0
    ALTERNATIVA_A_INDEX = 1
    ALTERNATIVA_B_INDEX = 2
    ALTERNATIVA_C_INDEX = 3
    RESPOSTA_CORRETA_INDEX = 4

    def __init__(self):
        super().__init__()
        self.title("Jogo de Perguntas e Respostas")  # Define o título da janela
        self.geometry("800x500")  # Define o tamanho da janela

        # Carrega a imagem de fundo com o Pillow
        self.background_image = Image.open("Untitled-design-19_resized.png")  # Substitua pelo caminho da sua imagem
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        # Cria um rótulo para exibir a imagem de fundo
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.place(relwidth=1, relheight=1)

        # Conecta ao banco de dados MySQL
        self.conexao = mysql.connector.connect(
            host="127.0.0.1",  # Substitua pelo seu host
            user="root",       # Substitua pelo seu usuário
            password="mualves",  # Substitua pela sua senha
            database="perguntas_respostas"  # Substitua pelo nome do seu banco de dados
        )

        # Cria um cursor para executar comandos SQL
        self.cursor = self.conexao.cursor()

        # Recupera perguntas do banco de dados
        self.perguntas = self.recuperar_perguntas_do_banco()
        self.pergunta_atual = 0

        # Configuração da interface gráfica
        self.label_pergunta = tk.Label(self, text="", font=("Arial", 14))  # Rótulo para exibir a pergunta
        self.label_pergunta.pack(pady=20)  # Empacota o rótulo na janela

        self.var_alternativa = tk.StringVar()  # Variável para controlar as respostas selecionadas
        self.var_alternativa.set("")  # Inicializa a variável

        self.alternativas = []  # Lista de botões de opção (radiobuttons)
        for i in range(3):
            alternativa = tk.Radiobutton(self, text="", variable=self.var_alternativa,
                                         value="", font=("Arial", 12))  # Cria um botão de opção
            alternativa.pack(anchor=tk.W)  # Empacota o botão na janela
            self.alternativas.append(alternativa)  # Adiciona o botão à lista

        self.btn_responder = tk.Button(self, text="Responder", command=self.verificar_resposta,
                                       font=("Arial", 12))  # Botão para responder à pergunta
        self.btn_responder.pack(pady=20)  # Empacota o botão na janela

        self.label_resultado = tk.Label(self, text="", font=("Arial", 14))  # Rótulo para exibir o resultado
        self.label_resultado.pack()  # Empacota o rótulo na janela

        # Inicializa os placares com zero
        self.pontos_corretos = 0  # Placar para respostas corretas
        self.pontos_errados = 0  # Placar para respostas erradas

        # Rótulo para exibir o placar de Respostas Corretas.
        self.label_placar_corretas = tk.Label(self, text="Respostas Corretas: 0", font=("Arial", 14))
        self.label_placar_corretas.pack()

        # Rótulo para exibir o placar de Respostas Erradas.
        self.label_placar_erradas = tk.Label(self, text="Respostas Erradas: 0", font=("Arial", 14))
        self.label_placar_erradas.pack()

        # Botão de reset
        self.btn_reset = tk.Button(self, text="Reiniciar Jogo", command=self.reiniciar_jogo, font=("Arial", 12))
        self.btn_reset.pack()

        # Inicia o jogo mostrando a primeira pergunta
        self.mostrar_pergunta_atual()

        # Impede que a janela seja redimensionada
        self.resizable(False, False)

    # Função para recuperar perguntas do banco de dados
    def recuperar_perguntas_do_banco(self):
        # Executa uma consulta SQL para recuperar todas as perguntas com alternativas
        self.cursor.execute("SELECT * FROM perguntas_alternativas")

        # Recupera todas as perguntas do banco de dados
        perguntas = self.cursor.fetchall()

        return perguntas

    ##############################################################################################################
    # Função para mostrar a pergunta atual na interface                                                          #
    # Esta função é responsável por atualizar a interface do jogo para exibir a pergunta atual,                  #
    # as alternativas de resposta e gerenciar o estado dos elementos da interface,                               #
    # como o rótulo da pergunta, os botões de opção (radiobuttons) e o botão "Responder".                        #
    ##############################################################################################################

    # Função para mostrar a pergunta atual na interface
    def mostrar_pergunta_atual(self):
        # Verifica se ainda há perguntas a serem mostradas
        if self.perguntas and self.pergunta_atual < len(self.perguntas):
            pergunta_atual = self.perguntas[self.pergunta_atual]  # Obtém a pergunta atual da lista de perguntas
            self.label_pergunta.config(
                text=pergunta_atual[1])  # Atualiza o rótulo para exibir a pergunta atual
            self.var_alternativa.set("")  # Limpa a seleção de respostas anteriores
            for i in range(3):
                # Configura os botões de opção (radiobuttons) com as alternativas da pergunta atual
                self.alternativas[i].config(text=pergunta_atual[i + 2],
                                            value=pergunta_atual[i + 2])
        else:
            # Caso não haja perguntas, exibe uma mensagem de fim de jogo
            self.label_pergunta.config(text="Fim do Jogo!")
            self.var_alternativa.set("")  # Limpa a seleção de respostas
            for i in range(3):
                # Remove o texto e desabilita os botões de opção
                self.alternativas[i].config(text="", value="")
            self.btn_responder.config(state=tk.DISABLED)  # Desabilita o botão "Responder"

    ##############################################################################################################
    # Função para verificar a resposta selecionada                                                               #
    # Esta função é responsável por verificar se a resposta selecionada pelo jogador está correta ou não,        #
    # atualizar o placar de pontos, exibir uma mensagem de resultado na interface e,                             #
    # em seguida, avançar para a próxima pergunta após um intervalo de tempo.                                    #
    ##############################################################################################################

    def verificar_resposta(self):
        # Obtém a pergunta atual da lista de perguntas
        pergunta_atual = self.perguntas[self.pergunta_atual]

        # Obtém a resposta selecionada pelo jogador
        resposta_selecionada = self.var_alternativa.get()

        # Obtém a resposta correta da pergunta atual no banco de dados
        resposta_correta = pergunta_atual[4]

        # Verifica se a resposta selecionada é igual à resposta correta da pergunta atual
        if resposta_selecionada == resposta_correta:
            # Se a resposta estiver correta, incrementa o placar de respostas corretas
            self.pontos_corretos += 1
        else:
            # Se a resposta estiver incorreta, incrementa o placar de respostas erradas
            self.pontos_errados += 1

        # Avança para a próxima pergunta
        self.pergunta_atual += 1

        # Atualiza os rótulos dos placares para exibir a pontuação atualizada
        self.label_placar_corretas.config(text=f"Respostas Corretas: {self.pontos_corretos}")
        self.label_placar_erradas.config(text=f"Respostas Erradas: {self.pontos_errados}")

        # Define um atraso de 1500 milissegundos (1,5 segundos) para mostrar a próxima pergunta
        self.after(1500, self.mostrar_pergunta_atual)

    ##############################################################################################################
    # Função para reiniciar o jogo e zerar o placar                                                              #
    # Neste código, foi adicionado um botão "Reiniciar Jogo" que chama a função reiniciar_jogo quando clicado.   #
    # A função reiniciar_jogo redefine a pergunta atual para a primeira,                                         #
    # zera o placar e atualiza o rótulo do placar. Isso permite que o jogador reinicie o jogo a qualquer momento.#
    ##############################################################################################################

    # Função para reiniciar o jogo e zerar os placares
    def reiniciar_jogo(self):
        self.pergunta_atual = 0  # Reinicia a pergunta para a primeira
        self.pontos_corretos = 0  # Zera o placar de respostas corretas
        self.pontos_errados = 0  # Zera o placar de respostas erradas
        self.label_placar_corretas.config(text="Respostas Corretas: 0")  # Atualiza o rótulo de respostas corretas
        self.label_placar_erradas.config(text="Respostas Erradas: 0")  # Atualiza o rótulo de respostas erradas
        self.mostrar_pergunta_atual()  # Mostra a primeira pergunta

        # Habilita o botão "Responder" para que o jogador possa responder novamente
        self.btn_responder.config(state=tk.NORMAL)

# Função principal
if __name__ == "__main__":
    jogo = JogoPerguntasRespostas()
    jogo.mainloop()
