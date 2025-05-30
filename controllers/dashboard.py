# controllers/dashboard.py - Nenhuma alteração significativa necessária para o roteamento

from flask import Blueprint, render_template, current_app, request, redirect, url_for
import os
import sys
import re
from utils.filetools import listar_projetos
import shutil # Certifique-se de que shutil está importado

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
        'Views': [],
        'Arquivos Estáticos': [],
        'Utilitários': [],
        'Outros Arquivos': [] # Adicionando uma categoria para outros arquivos
    }

    # Lista arquivos e diretórios ignorados
    ignore_list = ['.git', '.github', '__pycache__', '.venv', 'instance']

    for raiz, pastas, arquivos in os.walk(caminho):
        # Ignorar pastas na ignore_list
        pastas[:] = [p for p in pastas if p not in ignore_list and not p.startswith('.')]

        # Obter o caminho relativo da raiz atual
        caminho_rel_raiz = os.path.relpath(raiz, caminho)

        # Ignorar arquivos em pastas na ignore_list
        arquivos_filtrados = [a for a in arquivos if not any(ignored_dir in os.path.join(caminho_rel_raiz, a) for ignored_dir in ignore_list)]
        arquivos_filtrados = [a for a in arquivos_filtrados if not a.endswith('.pyc') and not a.endswith('.pyo')]


        for nome_arquivo in arquivos_filtrados:
            caminho_rel = os.path.join(caminho_rel_raiz, nome_arquivo)

            if 'models' in caminho_rel_raiz or 'model' in nome_arquivo.lower():
                estrutura['Modelos'].append(caminho_rel)
            elif 'controllers' in caminho_rel_raiz or 'controller' in nome_arquivo.lower():
                estrutura['Controladores'].append(caminho_rel)
            elif 'templates' in caminho_rel_raiz or nome_arquivo.lower().endswith('.html'): # Considera arquivos .html como Views
                estrutura['Views'].append(caminho_rel)
            elif 'static' in caminho_rel_raiz or any(nome_arquivo.lower().endswith(ext) for ext in ['.css', '.js', '.jpg', '.png', '.gif', '.svg']): # Adiciona arquivos estáticos
                 estrutura['Arquivos Estáticos'].append(caminho_rel)
            elif 'utils' in caminho_rel_raiz:
                 estrutura['Utilitários'].append(caminho_rel)
            else:
                # Adiciona outros arquivos que não se encaixam nas categorias acima
                estrutura['Outros Arquivos'].append(caminho_rel)


    # Ordenar arquivos dentro de cada categoria
    for categoria in estrutura:
        estrutura[categoria].sort()

    # Remover categorias vazias para uma apresentação mais limpa
    estrutura_limpa = {k: v for k, v in estrutura.items() if v}

    return render_template('projeto.html', nome=nome, estrutura=estrutura_limpa)


@dashboard_bp.route('/criar_projeto', methods=['POST'])
def criar_projeto():
    nome = request.form.get('nome')
    if nome:
        base = CAMINHO_PROJETOS()
        projeto_path = os.path.join(base, nome)
        if not os.path.exists(projeto_path):
            os.makedirs(projeto_path)

            # Estrutura mínima (verificar se já existem no código original e usar)
            estrutura = [
                'controllers',
                'models',
                'templates',
                'static/css',
                'static/js',
                'utils',
                'instance' # Adicionado instância para SQLite
            ]
            for pasta in estrutura:
                os.makedirs(os.path.join(projeto_path, pasta), exist_ok=True)

            # Carregar os templates de arquivos Python
            # Verifique se os caminhos dos templates estão corretos
            template_dir = os.path.join(os.path.dirname(__file__), '../utils')
            try:
                with open(os.path.join(template_dir, 'template_app.py'), 'r', encoding='utf-8') as f:
                    template_app = f.read()

                with open(os.path.join(template_dir, 'template_database.py'), 'r', encoding='utf-8') as f:
                    template_database = f.read()

                with open(os.path.join(template_dir, 'template_exemplo.py'), 'r', encoding='utf-8') as f:
                    template_exemplo = f.read()

                with open(os.path.join(template_dir, 'template_controller.py'), 'r', encoding='utf-8') as f:
                    template_controller = f.read()

            except FileNotFoundError as e:
                 # Se um template não for encontrado, registre o erro e continue ou retorne um erro
                 print(f"Erro ao carregar template: {e}")
                 # Dependendo da severidade, você pode querer retornar um erro para o usuário
                 # return render_template('error.html', mensagem=f"Erro interno: template não encontrado - {e}")
                 pass # Permite que o processo continue, mas arquivos podem faltar


            # Determinar o nome do blueprint a partir do template_controller.py
            blueprint_name = "main_bp" # Default
            if 'template_controller' in locals(): # Verifica se o template foi carregado
                try:
                    bp_match = re.search(r'(\w+)\s*=\s*Blueprint\(', template_controller)
                    if bp_match:
                        blueprint_name = bp_match.group(1)
                except Exception:
                    pass  # Manter o default se a busca falhar

            # Conteúdo simplificado para controllers/__init__.py
            # Assume que o app.py do projeto vai gerenciar sys.path se necessário
            controllers_init_py_content = f"""# Arquivo __init__.py para o pacote controllers
# Configurado para importar {blueprint_name} automaticamente
from .main_controller import {blueprint_name}
"""

            # Conteúdo genérico para outros __init__.py
            generic_init_py_content = "# Arquivo __init__.py para configurar o pacote"

            # Arquivos do projeto aprimorado com MVC e conexão de banco de dados
            # Use as variáveis carregadas ou um conteúdo padrão se o template falhou
            arquivos = {
                'app.py': locals().get('template_app', '# Conteúdo padrão para app.py\nfrom flask import Flask\napp = Flask(__name__)\n\n@app.route(\'/\')\ndef index():\n    return \'Projeto Flask criado!\''),
                'models/database.py': locals().get('template_database', '# Conteúdo padrão para database.py\n'),
                'models/exemplo.py': locals().get('template_exemplo', '# Conteúdo padrão para exemplo.py\n'),
                'controllers/main_controller.py': locals().get('template_controller', '# Conteúdo padrão para main_controller.py\nfrom flask import Blueprint\nmain_bp = Blueprint(\'main\', __name__)\n\n@main_bp.route(\'/\')\ndef index():\n    return \'Controller principal carregado!\''),
                # Templates HTML - Incluir conteúdo padrão ou carregar de templates se existirem
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
                'static/js/script.js': """// Script principal para funcionalidades do site

document.addEventListener('DOMContentLoaded', function() {
    console.log('Projeto Flask inicializado com sucesso!');

    // Adiciona classe ativa ao link atual
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');

    navLinks.forEach(link => {
        // Adiciona lógica para tratar a URL base do projeto
        // Pega o prefixo da URL (ex: /meu_projeto)
        const projectPrefix = window.location.pathname.split('/')[1];
        const linkHref = link.getAttribute('href');

        // Remove o prefixo do projeto do link href para comparação
        const cleanedLinkHref = linkHref.replace('/' + projectPrefix, '');

        // Verifica se o caminho atual (sem o prefixo do projeto) corresponde ao link
        if (currentPath.replace('/' + projectPrefix, '') === cleanedLinkHref) {
             link.parentElement.classList.add('active');
        }

         // Lida com a rota raiz do projeto (comparação especial para '/')
         if (currentPath === '/' + projectPrefix + '/' && linkHref === url_for('main.index')) {
            link.parentElement.classList.add('active');
         }
    });
});
"""
            }

            # Adicionar arquivos __init__.py para cada pacote Python
            init_dirs = [
                'controllers',
                'models',
                'utils',
                # Certifique-se que a pasta raiz do projeto também tem um __init__.py se ela for um pacote
                # '.' # Descomente se a raiz do projeto deve ser um pacote Python
            ]

            for init_dir in init_dirs:
                init_file_path = os.path.join(projeto_path, init_dir, '__init__.py')
                # Verifica se o diretório pai existe antes de criar o __init__.py
                if os.path.exists(os.path.dirname(init_file_path)):
                    if init_dir == 'controllers':
                         # Garante que o __init__.py do controllers importa o blueprint correto
                         with open(init_file_path, 'w', encoding='utf-8') as f:
                            f.write(controllers_init_py_content)
                    else:
                         # Para outros diretórios, usa o conteúdo genérico
                         with open(init_file_path, 'w', encoding='utf-8') as f:
                            f.write(generic_init_py_content)


            # Criar os arquivos do projeto
            for caminho, conteudo in arquivos.items():
                arquivo_full_path = os.path.join(projeto_path, caminho)
                os.makedirs(os.path.dirname(arquivo_full_path), exist_ok=True)
                # Adiciona verificação para não sobrescrever arquivos existentes acidentalmente
                if not os.path.exists(arquivo_full_path):
                    try:
                        with open(arquivo_full_path, 'w', encoding='utf-8') as f:
                            f.write(conteudo)
                    except Exception as e:
                         print(f"Erro ao criar arquivo {arquivo_full_path}: {e}")
                else:
                    print(f"Arquivo {arquivo_full_path} já existe, pulando criação.")


            # Criar banco de dados SQLite vazio na pasta instance
            instance_dir = os.path.join(projeto_path, 'instance')
            os.makedirs(instance_dir, exist_ok=True)
            db_path = os.path.join(instance_dir, 'database.db')
            if not os.path.exists(db_path):
                try:
                    import sqlite3
                    conn = sqlite3.connect(db_path)
                    conn.close()
                except Exception as e:
                    print(f"Erro ao criar banco de dados SQLite para {nome}: {e}")


    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/projeto/<nome>/arquivo/<path:path>', methods=['GET', 'POST'])
def editar_arquivo(nome, path):
    base = CAMINHO_PROJETOS()
    arquivo_path = os.path.join(base, nome, path)
    if request.method == 'POST':
        conteudo = request.form.get('conteudo')
        try:
            with open(arquivo_path, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            # Redireciona de volta para a página do projeto com uma mensagem de sucesso (opcional)
            return redirect(url_for('dashboard.projeto', nome=nome)) # Adicionar mensagem de sucesso seria bom
        except Exception as e:
            # Tratar erro ao salvar
            print(f"Erro ao salvar arquivo {arquivo_path}: {e}")
            # Renderiza a página de edição novamente com uma mensagem de erro
            try:
                with open(arquivo_path, 'r', encoding='utf-8') as f:
                     conteudo_atual = f.read()
            except:
                 conteudo_atual = "Não foi possível ler o arquivo após o erro."
            return render_template('editar_arquivo.html',
                                   nome=nome,
                                   path=path,
                                   conteudo=conteudo_atual,
                                   erro=f"Erro ao salvar arquivo: {str(e)}"), 500 # Retorna status code 500


    # Método GET
    try:
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except FileNotFoundError:
        conteudo = '' # Arquivo não encontrado, editor vazio
        # Opcional: Retornar um 404 ou uma mensagem indicando que o arquivo não existe
    except Exception as e:
        # Tratar outros erros de leitura
        conteudo = f"# Erro ao ler arquivo: {str(e)}"
        return render_template('editar_arquivo.html',
                               nome=nome,
                               path=path,
                               conteudo=conteudo,
                               erro=f"Erro ao ler arquivo: {str(e)}"), 500


    # Passa a linha de erro para o template, se existir na URL (redirecionado da execução)
    error_line = request.args.get('errorLine')

    return render_template('editar_arquivo.html', nome=nome, path=path, conteudo=conteudo, errorLine=error_line)

@dashboard_bp.route('/deletar_projeto/<nome>', methods=['POST'])
def deletar_projeto(nome):

    base = CAMINHO_PROJETOS()
    projeto_path = os.path.join(base, nome)

    if os.path.exists(projeto_path) and os.path.isdir(projeto_path):
        try:
            shutil.rmtree(projeto_path)
            # Opcional: Adicionar mensagem de sucesso
        except Exception as e:
            # Em caso de erro, registre em log ou mostre mensagem de erro para o usuário
            print(f"Erro ao deletar projeto {nome}: {e}")
            # Pode redirecionar para a página principal com uma mensagem de erro
            # return redirect(url_for('dashboard.index', erro=f"Erro ao excluir projeto {nome}: {str(e)}"))
            pass # Continua o redirecionamento para a página principal

    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/projeto/<nome>/deploy')
def deploy_guide(nome):
    """Exibe um guia de como implantar o projeto no PythonAnywhere"""
    return render_template('deploy_guide.html', nome=nome)

@dashboard_bp.route('/projeto/<nome>/reparar', methods=['GET', 'POST'])
def reparar_projeto(nome):
    """Repara um projeto existente adicionando os arquivos que faltam"""
    base = CAMINHO_PROJETOS()
