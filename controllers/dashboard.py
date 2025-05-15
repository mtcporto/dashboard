from flask import Blueprint, render_template
import os
from utils.filetools import listar_projetos

dashboard_bp = Blueprint('dashboard', __name__)
CAMINHO_PROJETOS = os.path.join(os.path.dirname(__file__), '..', 'meus_projetos')

@dashboard_bp.route('/')
def index():
    projetos = listar_projetos(CAMINHO_PROJETOS)
    return render_template('home.html', projetos=projetos)

@dashboard_bp.route('/projeto/<nome>')
def projeto(nome):
    caminho = os.path.join(CAMINHO_PROJETOS, nome)
    estrutura = []

    for raiz, pastas, arquivos in os.walk(caminho):
        for nome_arquivo in arquivos:
            caminho_rel = os.path.relpath(os.path.join(raiz, nome_arquivo), caminho)
            estrutura.append(caminho_rel)

    return render_template('projeto.html', nome=nome, arquivos=estrutura)
