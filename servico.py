from flask import Flask, Response, request
from robo import *

import json

sucesso, robo, artigos = inicializar()
servico = Flask(NOME_ROBO)

INFO = {
    "descricao": "Robô Bibliotecário Akhenaton. Realiza atendimentos a usuários de uma biblioteca.",
    "versao": "1.0"
}

@servico.get("/")
def get_info():
    return Response(json.dumps(INFO), status=200, mimetype="application/json")

@servico.get("/alive")
def is_alive():
    return Response(json.dumps({"alive": "sim" if sucesso else "não"}), status=200, mimetype="application/json")

@servico.post("/responder")
def get_resposta():
    if sucesso:
        conteudo = request.json
        resposta = robo.get_response(conteudo["pergunta"])

        return Response(json.dumps({"resposta": resposta.text, "confianca": resposta.confidence}), status=200, mimetype="application/json")
    else:
        return Response(status=503)
    
@servico.post("/artigos")
def get_artigos():
    encontrou, artigos_selecionados = False, []

    conteudo = request.json
    modo = conteudo["modo"]

    criterios = [conteudo['criterio1'], conteudo['criterio2'], conteudo['criterio3'], conteudo['criterio4'], conteudo['criterio5'], conteudo['criterio6'], conteudo['criterio7']]

    encontrou, artigos_selecionados = pesquisar_artigos_por_chaves(criterios, artigos) if modo == "chaves" else pesquisar_artigos_por_areas(criterios, artigos)

    return Response(json.dumps({"artigos": list(artigos_selecionados.values())}), status=200 if encontrou else 204, mimetype="application/json")


if __name__ == "__main__":
    servico.run(host="0.0.0.0", port=5000, debug=True)