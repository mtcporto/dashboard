from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

BASE_DIR = os.path.join(os.path.dirname(__file__), 'meus_projetos')

@app.route('/')
def index():
    projetos = os.listdir(BASE_DIR)
    projetos = [p for p in projetos if os.path.isdir(os.path.join(BASE_DIR, p))]

    # Adiciona o próprio dashboard como um projeto
    projetos.append('dashboard (este projeto)')

    return render_template('index.html', projetos=projetos)


@app.route('/criar_projeto', methods=['POST'])
def criar_projeto():
    nome = request.form.get('nome')
    if nome:
        projeto_path = os.path.join(BASE_DIR, nome)
        if not os.path.exists(projeto_path):
            os.makedirs(projeto_path)

            # Estrutura mínima
            estrutura = [
                'controllers',
                'utils',
                'static/css',
                'static/js',
                'templates'
            ]
            for pasta in estrutura:
                os.makedirs(os.path.join(projeto_path, pasta), exist_ok=True)

            # Arquivos iniciais
            arquivos = {
                'app.py': "# Arquivo principal do projeto\n\nfrom flask import Flask\n\napp = Flask(__name__)\n",
                'controllers/dashboard.py': "# Controlador inicial\n",
                'utils/filetools.py': "# Funções auxiliares para manipulação de arquivos\n",
                'templates/base.html': "<!-- HTML base -->\n<!DOCTYPE html>\n<html><body>{% block content %}{% endblock %}</body></html>",
                'templates/home.html': "{% extends 'base.html' %}\n{% block content %}<h1>Home</h1>{% endblock %}",
                'templates/projeto.html': "{% extends 'base.html' %}\n{% block content %}<h1>Projeto</h1>{% endblock %}",
            }
            for caminho, conteudo in arquivos.items():
                arquivo_path = os.path.join(projeto_path, caminho)
                with open(arquivo_path, 'w') as f:
                    f.write(conteudo)
    return redirect(url_for('index'))

@app.route('/projeto/<nome>/')
def visualizar_projeto(nome):
    projeto_path = os.path.join(BASE_DIR, nome)
    arquivos = []
    for root, dirs, files in os.walk(projeto_path):
        for file in files:
            full_path = os.path.relpath(os.path.join(root, file), projeto_path)
            arquivos.append(full_path)
    return render_template('projeto.html', nome=nome, arquivos=arquivos)
