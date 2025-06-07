from nltk import word_tokenize, corpus
from nltk.corpus import floresta

from collections import Counter
from string import punctuation

import sqlite3
import os

CAMINHO_ARTIGOS = "/misc/ifba/workspaces/sistemas especialistas/bibliotecario/artigos"
CAMINHO_BD = "/misc/ifba/workspaces/sistemas especialistas/bibliotecario"
BD_ARTIGOS = f"{CAMINHO_BD}/artigos.sqlite3"

PALAVRAS_CHAVE_POR_ARTIGO = 7
FREQUENCIA_MINIMA = 2

REMOVIVEIS_LATEX = [
    "\\textbf",
    "\\textit",
    "{",
    "}"
]

CLASSES_GRAMATICAIS_INDESEJADAS = [
    "adv",
    "v-inf",
    "v-fin",
    "v-pcp",
    "v-ger",
    "num",
    "adj"
]

def inicializar():
    palavras_de_parada = set(corpus.stopwords.words("portuguese"))

    classificacoes = {}
    for (palavra, classificacao) in floresta.tagged_words():
        classificacoes[palavra.lower()] = classificacao

    return palavras_de_parada, classificacoes

def ler_conteudo(artigo):
    sucesso, conteudo = False, None

    try:
        with open(artigo, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read()

            arquivo.close()

        sucesso = True
    except Exception as e:
        print(f"erro lendo conteúdo do artigo: {str(e)}")

    return sucesso, conteudo

def extrair_titulo(conteudo):
    marcador = "\\title{"
    marcador = conteudo.index(marcador) + len(marcador)

    titulo = conteudo[marcador:]
    titulo = titulo[:titulo.index("}")]

    return titulo

def extrair_resumo(conteudo):
    marcador_inicio, marcador_fim = "\\begin{resumo}", "\\end{resumo}"

    marcador_inicio = conteudo.index(marcador_inicio) + len(marcador_inicio)
    marcador_fim = conteudo.index(marcador_fim)

    resumo = conteudo[marcador_inicio:marcador_fim]

    return resumo

def eliminar_palavras_de_parada(tokens, palavras_de_parada):
    tokens_filtrados = []

    for token in tokens:
        if token not in palavras_de_parada:
            tokens_filtrados.append(token)

    return tokens_filtrados

def eliminar_marcacoes_latex(tokens):
    tokens_filtrados = []

    for token in tokens:
        if token not in REMOVIVEIS_LATEX:
            tokens_filtrados.append(token)

    return tokens_filtrados

def eliminar_pontuacoes(tokens):
    tokens_filtrados = []

    for token in tokens:
        if token not in punctuation:
            tokens_filtrados.append(token)

    return tokens_filtrados

def eliminar_classes_gramaticais(tokens, classificacoes):
    tokens_filtrados = []

    for token in tokens:
        if token in classificacoes.keys():
            classificacao = classificacoes[token]
            if not any (s in classificacao for s in CLASSES_GRAMATICAIS_INDESEJADAS):
                tokens_filtrados.append(token)
        else:
            tokens_filtrados.append(token)

    return tokens_filtrados

def eliminar_frequencias_baixas(tokens):
    tokens_filtrados, frequencias = [], Counter(tokens)

    for token, frequencia in frequencias.most_common():
        if frequencia >= FREQUENCIA_MINIMA:
            tokens_filtrados.append(token)

    return tokens_filtrados

def iniciar_banco_artigos():
    if os.path.exists(BD_ARTIGOS):
        os.remove(BD_ARTIGOS)

    conexao = sqlite3.connect(BD_ARTIGOS)

    cursor = conexao.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS artigos(id INTEGER, titulo TEXT, artigo TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS chaves(id_artigo INTEGER, chave1 TEXT, chave2 TEXT, chave3 TEXT, chave4 TEXT, chave5 TEXT, chave6 TEXT, chave7 TEXT)")

    conexao.close()

def gravar_artigo(id_artigo, titulo, chaves, artigo):
    conexao = sqlite3.connect(BD_ARTIGOS)
    cursor = conexao.cursor()

    insert = f"INSERT INTO artigos(id, titulo, artigo) VALUES({id_artigo}, '{titulo}', '{artigo}')"
    cursor.execute(insert)

    while len(chaves) < PALAVRAS_CHAVE_POR_ARTIGO:
        chaves.append("")

    insert = f"INSERT INTO chaves(id_artigo, chave1, chave2, chave3, chave4, chave5, chave6, chave7) VALUES ({id_artigo}"
    for contador, chave in enumerate(chaves):
        insert += f", '{chave}'"

        if contador + 1 == PALAVRAS_CHAVE_POR_ARTIGO:
            break
    insert += ")"
    cursor.execute(insert)

    conexao.commit()
    conexao.close()

MAXIMO_ARTIGO = 1_000

if __name__ == "__main__":
    palavras_de_parada, classificacoes = inicializar()

    iniciar_banco_artigos()

    for contador in range(1, MAXIMO_ARTIGO):
        tex = f"{contador}.tex"
        pdf = f"{contador}.pdf"
        caminho_artigo = f"{CAMINHO_ARTIGOS}/{tex}"

        if os.path.exists(caminho_artigo):
            sucesso, conteudo = ler_conteudo(caminho_artigo)

            if sucesso:
                titulo = extrair_titulo(conteudo)
                # print(f"título do artigo: {titulo}")
                resumo = extrair_resumo(conteudo)
                print(f"resumo: {resumo}")

                tokens = word_tokenize(resumo.lower())
                tokens = eliminar_palavras_de_parada(tokens, palavras_de_parada)
                tokens = eliminar_marcacoes_latex(tokens)
                tokens = eliminar_pontuacoes(tokens)
                tokens = eliminar_classes_gramaticais(tokens, classificacoes)
                tokens = eliminar_frequencias_baixas(tokens)
                # print(f"tokens filtrados: {tokens}")

                gravar_artigo(contador, titulo, tokens, pdf)
        else:
            break