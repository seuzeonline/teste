import json
import time
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_servidores(nome_servidor):
    url = "https://api.imap.org.br/api/DespesaPessoal?cod_orgao_org=1784"
    start_time = time.time()

    try:
        response = requests.get(url, headers={"accept": "text/plain"}, timeout=10)
        data = response.json()

        servidores_filtrados = [
            servidor for servidor in data if nome_servidor.lower() in servidor["des_nome_servidor_sa2"].lower()
        ]

        if time.time() - start_time > 10:
            return {"error": "A consulta excedeu o tempo limite de 10 segundos"}, 408

        return {"servidores": servidores_filtrados}, 200

    except requests.exceptions.Timeout:
        return {"error": "A requisição excedeu o tempo de espera"}, 408
    except Exception as e:
        return {"error": f"Ocorreu um erro: {str(e)}"}, 500

@app.route('/api/servidores', methods=['GET'])
def servidores():
    nome_servidor = request.args.get('nome_servidor')

    if not nome_servidor:
        return jsonify({"error": "Nome do servidor é obrigatório"}), 400

    return jsonify(get_servidores(nome_servidor)[0])

# Vercel usa o handler para funções serverless
def handler(request):
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    from werkzeug.wrappers import Request
    from werkzeug.serving import run_simple

    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/api': app
    })
    
    request = Request(request.environ)
    response = app.full_dispatch_request()
    return response

# Isso é necessário para que o Vercel reconheça a aplicação Flask
if __name__ == "__main__":
    app.run(debug=True)
