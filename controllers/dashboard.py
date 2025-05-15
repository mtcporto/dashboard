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
    estrutura = {
        'Modelos': [],
        'Controladores': [],
        'Views': []
    }

    for raiz, pastas, arquivos in os.walk(caminho):
        # Ignorar pastas desnecessárias
        pastas[:] = [p for p in pastas if p not in ['.git', '.github']]
        
        # Filtrar arquivos de cache e outros arquivos desnecessários
        arquivos_filtrados = [a for a in arquivos if not a.endswith('.pyc') and not a.endswith('.pyo')]
        
        for nome_arquivo in arquivos_filtrados:
            caminho_rel = os.path.relpath(os.path.join(raiz, nome_arquivo), caminho)
            
            # Ignorar arquivos em pastas __pycache__
            if '__pycache__' in caminho_rel:
                continue
                
            if 'models' in raiz or 'model' in caminho_rel:
                estrutura['Modelos'].append(caminho_rel)
            elif 'controllers' in raiz or 'controller' in caminho_rel:
                estrutura['Controladores'].append(caminho_rel)
            elif 'templates' in raiz or 'view' in caminho_rel:
                estrutura['Views'].append(caminho_rel)

    return render_template('projeto.html', nome=nome, estrutura=estrutura)

@dashboard_bp.route('/criar_projeto', methods=['POST'])
def criar_projeto():
    nome = request.form.get('nome')
    if nome:
        base = CAMINHO_PROJETOS()
        projeto_path = os.path.join(base, nome)
        if not os.path.exists(projeto_path):
            os.makedirs(projeto_path)
            
            # Estrutura mínima
            estrutura = [
                'controllers',
                'models',
                'templates',
                'static/css',
                'static/js',
                'utils'
            ]
            for pasta in estrutura:
                os.makedirs(os.path.join(projeto_path, pasta), exist_ok=True)
            
            # Arquivos do Hello World
            arquivos = {
                'app.py': """from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', mensagem='Hello World!')

if __name__ == '__main__':
    app.run(debug=True)
""",
                'templates/index.html': """<!DOCTYPE html>
<html>
<head>
    <title>{{ mensagem }}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>{{ mensagem }}</h1>
        <p>Bem-vindo ao seu novo projeto Flask!</p>
    </div>
</body>
</html>
""",
                'templates/base.html': """<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Meu Projeto{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block head %}{% endblock %}
</head>
<body>
    <header>
        <nav>
            <a href="/">Início</a>
        </nav>
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
    <footer>
        <p>&copy; {{ current_year }} Meu Projeto</p>
    </footer>
</body>
</html>
""",
                'static/css/style.css': """body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
    color: #333;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background-color: white;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h1 {
    color: #2c3e50;
}
"""
            }
            
            for caminho, conteudo in arquivos.items():
                arquivo_full_path = os.path.join(projeto_path, caminho)
                os.makedirs(os.path.dirname(arquivo_full_path), exist_ok=True)
                with open(arquivo_full_path, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                    
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

@dashboard_bp.route('/deletar_projeto/<nome>', methods=['POST'])
def deletar_projeto(nome):
    import shutil
    
    base = CAMINHO_PROJETOS()
    projeto_path = os.path.join(base, nome)
    
    if os.path.exists(projeto_path) and os.path.isdir(projeto_path):
        try:
            shutil.rmtree(projeto_path)
        except Exception as e:
            # Em caso de erro, poderia registrar em log ou mostrar mensagem
            pass
            
    return redirect(url_for('dashboard.index'))
