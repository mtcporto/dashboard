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
            
            # Carregar os templates de arquivos Python
            with open(os.path.join(os.path.dirname(__file__), '../utils/template_app.py'), 'r') as f:
                template_app = f.read()
                
            with open(os.path.join(os.path.dirname(__file__), '../utils/template_database.py'), 'r') as f:
                template_database = f.read()
                
            with open(os.path.join(os.path.dirname(__file__), '../utils/template_exemplo.py'), 'r') as f:
                template_exemplo = f.read()
                
            with open(os.path.join(os.path.dirname(__file__), '../utils/template_controller.py'), 'r') as f:
                template_controller = f.read()
            
            # Arquivos do projeto aprimorado com MVC e conexão de banco de dados
            arquivos = {
                # App principal com roteamento para acesso via URL direta (/nome_do_projeto)
                'app.py': template_app,
                
                # Modelo de banco de dados SQLAlchemy
                'models/database.py': template_database,
                
                # Modelo de exemplo
                'models/exemplo.py': template_exemplo,
                
                # Controlador principal
                'controllers/main_controller.py': template_controller,
                # Template base
                'templates/base.html': """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Projeto Flask{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block head %}{% endblock %}
</head>
<body>
    <header>
        <nav>
            <div class="container">
                <div class="logo">Projeto Flask</div>
                <ul class="nav-links">
                    <li><a href="{{ url_for('main.index') }}">Início</a></li>
                    <li><a href="{{ url_for('main.sobre') }}">Sobre</a></li>
                </ul>
            </div>
        </nav>
    </header>
    
    <main>
        <div class="container">
            {% block content %}{% endblock %}
        </div>
    </main>
    
    <footer>
        <div class="container">
            <p>&copy; {{ now.year if now else '2025' }} Projeto Flask</p>
        </div>
    </footer>
    
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
""",
                # Template index
                'templates/index.html': """{% extends "base.html" %}

{% block title %}Início | Projeto Flask{% endblock %}

{% block content %}
<div class="welcome-section">
    <h1>Bem-vindo ao seu novo Projeto Flask!</h1>
    <p class="lead">Este projeto foi criado com um scaffold MVC completo, pronto para desenvolvimento.</p>
    
    <div class="features">
        <div class="feature-card">
            <h3>SQLAlchemy</h3>
            <p>Banco de dados configurado com SQLAlchemy, pronto para criar modelos e fazer consultas.</p>
        </div>
        
        <div class="feature-card">
            <h3>Blueprints</h3>
            <p>Estrutura organizada com blueprints para facilitar o crescimento do projeto.</p>
        </div>
        
        <div class="feature-card">
            <h3>Templates</h3>
            <p>Sistema de templates Jinja2 com herança e blocos predefinidos.</p>
        </div>
    </div>
    
    <div class="cta-section">
        <h2>Como começar?</h2>
        <ol>
            <li>Explore os arquivos na estrutura MVC</li>
            <li>Crie novos modelos baseados no exemplo</li>
            <li>Adicione novas rotas aos controladores</li>
            <li>Desenvolva templates para suas views</li>
        </ol>
    </div>
</div>
{% endblock %}
""",
                # Template sobre
                'templates/sobre.html': """{% extends "base.html" %}

{% block title %}Sobre | Projeto Flask{% endblock %}

{% block content %}
<div class="about-section">
    <h1>Sobre este Projeto</h1>
    
    <p>Este é um projeto Flask criado com estrutura MVC. Foi gerado automaticamente pelo Dashboard de Projetos.</p>
    
    <h2>Recursos do Projeto</h2>
    <ul>
        <li>Estrutura MVC (Model-View-Controller) organizada</li>
        <li>SQLAlchemy para ORM e interação com banco de dados</li>
        <li>Templates com herança usando Jinja2</li>
        <li>CSS básico com design responsivo</li>
        <li>API REST básica para demonstração</li>
    </ul>
    
    <h2>Tecnologias</h2>
    <ul>
        <li>Python</li>
        <li>Flask</li>
        <li>SQLAlchemy</li>
        <li>HTML5 & CSS3</li>
        <li>JavaScript</li>
    </ul>
</div>
{% endblock %}
""",
                # CSS
                'static/css/style.css': """/* Estilos Gerais */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

.container {
    width: 90%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}

h1, h2, h3, h4, h5, h6 {
    margin-bottom: 0.8rem;
    color: #2c3e50;
}

p {
    margin-bottom: 1rem;
}

a {
    color: #3498db;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* Header e Navegação */
header {
    background-color: #2c3e50;
    color: white;
    padding: 1rem 0;
    margin-bottom: 2rem;
}

nav .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
}

.nav-links {
    display: flex;
    list-style: none;
}

.nav-links li {
    margin-left: 1.5rem;
}

.nav-links a {
    color: white;
}

/* Seção de Boas-vindas */
.welcome-section {
    margin-bottom: 2rem;
}

.lead {
    font-size: 1.2rem;
    margin-bottom: 1.5rem;
}

/* Cards de recursos */
.features {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.feature-card {
    background-color: white;
    padding: 1.5rem;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

/* Seção CTA */
.cta-section {
    background-color: #f1f8ff;
    padding: 1.5rem;
    border-radius: 5px;
    border-left: 4px solid #3498db;
    margin: 2rem 0;
}

.cta-section ol {
    margin-left: 1.5rem;
}

/* Seção Sobre */
.about-section h2 {
    margin-top: 2rem;
}

.about-section ul {
    margin-left: 1.5rem;
    margin-bottom: 1.5rem;
}

/* Footer */
footer {
    text-align: center;
    padding: 1.5rem 0;
    margin-top: 3rem;
    background-color: #2c3e50;
    color: white;
}

/* Responsivo */
@media (max-width: 768px) {
    .features {
        grid-template-columns: 1fr;
    }
}
""",
                # JavaScript
                'static/js/script.js': """// Script principal para funcionalidades do site

document.addEventListener('DOMContentLoaded', function() {
    console.log('Projeto Flask inicializado com sucesso!');
    
    // Adiciona classe ativa ao link atual
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.parentElement.classList.add('active');
        }
    });
});
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
