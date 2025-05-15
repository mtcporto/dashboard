from flask import Blueprint, render_template, current_app, request, redirect, url_for
import os
from utils.filetools import listar_projetos

dashboard_bp = Blueprint('dashboard', __name__)
# projects directory is configured in app.config['BASE_DIR']
CAMINHO_PROJETOS = lambda: current_app.config['BASE_DIR']

@dashboard_bp.route('/')
def index():
    projetos = listar_projetos(CAMINHO_PROJETOS())
    return render_template('home.html', projetos=projetos)

@dashboard_bp.route('/projeto/<nome>')
def projeto(nome):
    caminho = os.path.join(CAMINHO_PROJETOS(), nome)
    estrutura = []

    for raiz, pastas, arquivos in os.walk(caminho):
        for nome_arquivo in arquivos:
            caminho_rel = os.path.relpath(os.path.join(raiz, nome_arquivo), caminho)
            estrutura.append(caminho_rel)

    return render_template('projeto.html', nome=nome, arquivos=estrutura)

@dashboard_bp.route('/criar_projeto', methods=['POST'])
def criar_projeto():
    nome = request.form.get('nome')
    if nome:
        base = CAMINHO_PROJETOS()
        projeto_path = os.path.join(base, nome)
        if not os.path.exists(projeto_path):
            os.makedirs(projeto_path)
            # Estrutura mínima
            estrutura = ['controllers', 'utils', 'static/css', 'static/js', 'templates']
            for pasta in estrutura:
                os.makedirs(os.path.join(projeto_path, pasta), exist_ok=True)
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/projeto/<nome>/arquivo/<path:path>', methods=['GET', 'POST'])
def editar_arquivo(nome, path):
    base = CAMINHO_PROJETOS()
    arquivo_path = os.path.join(base, nome, path)
    if request.method == 'POST':
        conteudo = request.form.get('conteudo')
        with open(arquivo_path, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        return redirect(url_for('dashboard.projeto', nome=nome))
    try:
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except FileNotFoundError:
        conteudo = ''
    return render_template('editar_arquivo.html', nome=nome, path=path, conteudo=conteudo)
