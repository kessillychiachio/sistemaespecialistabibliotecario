from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

import json

CONVERSAS = [
    "/misc/ifba/workspaces/sistemas especialistas/bibliotecario/conversas/saudacoes.json",
    "/misc/ifba/workspaces/sistemas especialistas/bibliotecario/conversas/informacoes_basicas.json",
    "/misc/ifba/workspaces/sistemas especialistas/bibliotecario/conversas/comandos_pesquisa.json"
]

NOME_ROBO = "Robô Bibliotecário Akhenaton"
BD_ROBO = "chat.sqlite3"

def criar_treinador():
    robo = ChatBot(NOME_ROBO, storage_adapter = "chatterbot.storage.SQLStorageAdapter", database_uri=f"sqlite:///{BD_ROBO}")
    robo.storage.drop()

    return ListTrainer(robo)

def carregar_conversas():
    conversas = []

    for arquivo_conversas in CONVERSAS:
        with open(arquivo_conversas, "r", encoding="utf-8") as arquivo:
            lista_conversas = json.load(arquivo)
            conversas.append(lista_conversas["conversas"])

            arquivo.close()

    return conversas

def treinar(treinador, conversas):
    for conversa in conversas:
        for mensagens_resposta in conversa:
            mensagens = mensagens_resposta["mensagens"]
            resposta = mensagens_resposta["resposta"]

            for mensagem in mensagens:
                print(f"treinando mensagem: {mensagem}, resposta: {resposta}")

                treinador.train([mensagem, resposta])

if __name__ == "__main__":
    treinador = criar_treinador()
    conversas = carregar_conversas()
    if treinador and conversas:
        treinar(treinador, conversas)
