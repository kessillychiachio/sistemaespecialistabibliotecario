from PIL import Image
import pytesseract
import sqlite3
import os

from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

MODELO = "models/gemini-1.5-flash"
MAXIMO_IMAGENS = 1_000
CAMINHO_IMAGENS = "/Users/anakchiachio/Desktop/IFBA/2semestre/Sistemas Especialistas/bibliotecario/artigos"
CAMINHO_BD = "/Users/anakchiachio/Desktop/IFBA/2semestre/Sistemas Especialistas/bibliotecario"
BD_ARTIGOS = f"{CAMINHO_BD}/artigos.sqlite3"
AREAS_POR_ARTIGO = 7

with open("genai.key", "r") as chave:
    API_KEY = chave.read().strip()
    
def inicializar():
    inicializado, corretor_gramatical = False, None

    try:
        corretor_gramatical = ChatGoogleGenerativeAI(
            model=MODELO,
            google_api_key=API_KEY
        )

        conexao = sqlite3.connect(BD_ARTIGOS)
        cursor = conexao.cursor()
        cursor.execute("DROP TABLE IF EXISTS areas")
        cursor.execute("CREATE TABLE areas(id_artigo INTEGER, area1 TEXT, area2 TEXT, area3 TEXT, area4 TEXT, area5 TEXT, area6 TEXT, area7 TEXT)")
        conexao.close()

        inicializado = True
    except Exception as e:
        print(f"erro inicializando: {str(e)}")

    return inicializado, corretor_gramatical

def get_areas_de_conhecimento(imagem, corretor_gramatical):
    areas_corrigidas = []

    texto = pytesseract.image_to_string(Image.open(imagem), lang="por")
    areas = texto.split("\n")
    areas = [area for area in areas if area != '']

    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Você é um assistente especialista em revisão técnica de artigos acadêmicos."),
            ("system", "Corrija gramaticalmente e ortograficamente os nomes de áreas de conhecimento fornecidos."),
            ("system", "Mantenha o sentido acadêmico original e a capitalização correta."),
            ("system", "Use vírgula para separar os nomes."),
            ("system", "Responda apenas com a lista de nomes corrigidos, separados por vírgula, sem explicações ou comentários."),
            ("human", "{entrada}")
        ])

        mensagens = prompt.format_messages(entrada=", ".join(areas))
        resposta = corretor_gramatical.invoke(mensagens)
        if resposta and resposta.content:
            areas_corrigidas = [a.strip() for a in resposta.content.split(",") if a.strip()]
    except Exception as e:
        print(f"Erro ao corrigir áreas: {str(e)}")

    return areas_corrigidas

def gravar_areas(id_artigo, areas):
    conexao = sqlite3.connect(BD_ARTIGOS)
    cursor = conexao.cursor()

    while len(areas) < AREAS_POR_ARTIGO:
        areas.append("")

    insert = f"INSERT INTO areas(id_artigo, area1, area2, area3, area4, area5, area6, area7) VALUES ({id_artigo}"
    for contador, area in enumerate(areas[:AREAS_POR_ARTIGO]):
        insert += f", '{area.lower()}'"
    insert += ")"

    cursor.execute(insert)
    conexao.commit()
    conexao.close()

def visualizar_areas():
    conexao = sqlite3.connect(BD_ARTIGOS)
    cursor = conexao.cursor()
    cursor.execute("SELECT id, titulo, area1, area2, area3, area4, area5, area6, area7 FROM artigos, areas WHERE areas.id_artigo = artigos.id")
    artigos = cursor.fetchall()
    conexao.close()

    return artigos

if __name__ == "__main__":
    inicializado, corretor_gramatical = inicializar()

    if inicializado:
        for contador in range(1, MAXIMO_IMAGENS):
            imagem = f"{CAMINHO_IMAGENS}/{contador}.disciplinas.png"
            if os.path.exists(imagem):
                print(f"processando a imagem: {imagem}")
                areas = get_areas_de_conhecimento(imagem, corretor_gramatical)

                print(f"áreas encontradas: {areas}")

                gravar_areas(contador, areas)
            else:
                break

    print(f"areas por artigos: {visualizar_areas()}")
