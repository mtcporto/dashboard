from flask import Blueprint, render_template, current_app, request, redirect, url_for
import os
import sys # Added import
import re # Added import
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
                
            # Criar arquivos __init__.py para evitar erros de importação
            # init_py_content = "# Arquivo __init__.py para configurar o pacote" # Old content
            
            # Determinar o nome do blueprint a partir do template_controller.py
            blueprint_name = "main_bp" # Default
            try:
                bp_match = re.search(r'(\w+)\s*=\s*Blueprint\(', template_controller)
                if bp_match:
                    blueprint_name = bp_match.group(1)
            except Exception:
                pass  # Manter o default se a busca falhar

            # Conteúdo simplificado para controllers/__init__.py
            # Relies on app.py (from template_app.py) to set up sys.path correctly.
            controllers_init_py_content = f"""# Arquivo __init__.py para o pacote controllers
# Configurado para importar {blueprint_name} automaticamente
from .main_controller import {blueprint_name}
"""
            
            # Conteúdo genérico para outros __init__.py
            generic_init_py_content = "# Arquivo __init__.py para configurar o pacote"

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
            
            # Adicionar arquivos __init__.py para cada pacote Python
            init_dirs = [
                'controllers',
                'models',
                'utils'
            ]
            
            for init_dir in init_dirs:
                init_file_path = os.path.join(projeto_path, init_dir, '__init__.py')
                os.makedirs(os.path.dirname(init_file_path), exist_ok=True)
                with open(init_file_path, 'w', encoding='utf-8') as f:
                    if init_dir == 'controllers':
                        f.write(controllers_init_py_content)
                    else:
                        f.write(generic_init_py_content)
            
            # Criar os arquivos do projeto
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
    import shutil # Added import
    
    base = CAMINHO_PROJETOS()
    projeto_path = os.path.join(base, nome)
    
    if os.path.exists(projeto_path) and os.path.isdir(projeto_path):
        try:
            shutil.rmtree(projeto_path)
        except Exception as e:
            # Em caso de erro, poderia registrar em log ou mostrar mensagem
            pass
            
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/projeto/<nome>/deploy')
def deploy_guide(nome):
    """Exibe um guia de como implantar o projeto no PythonAnywhere"""
    return render_template('deploy_guide.html', nome=nome)

@dashboard_bp.route('/projeto/<nome>/reparar', methods=['GET', 'POST'])
def reparar_projeto(nome):
    """Repara um projeto existente adicionando os arquivos que faltam"""
    base = CAMINHO_PROJETOS()
    projeto_path = os.path.join(base, nome)
    
    if not os.path.exists(projeto_path) or not os.path.isdir(projeto_path):
        return render_template('projeto_error.html', nome=nome, 
                              erro="Projeto não encontrado. Não foi possível reparar."), 404
    
    # Verificar e corrigir o app.py do projeto para resolver problemas de importação comuns
    app_path = os.path.join(projeto_path, 'app.py')
    app_fixed = False
    
    if os.path.exists(app_path):
        try:
            with open(app_path, 'r') as f:
                app_content = f.read()
            
            # Verifica problemas comuns de importação do controlador
            if "from controllers import main_controller" in app_content:
                app_content = app_content.replace(
                    "from controllers import main_controller", 
                    "from controllers.main_controller import main_bp")
                app_fixed = True
            elif "import controllers.main_controller" in app_content and "main_bp" not in app_content:
                app_content = app_content.replace(
                    "import controllers.main_controller", 
                    "from controllers.main_controller import main_bp")
                app_fixed = True
            elif "controllers.main_controller" in app_content and "register_blueprint" in app_content and "main_bp" not in app_content:
                app_content = app_content.replace(
                    "controllers.main_controller", 
                    "controllers.main_controller.main_bp")
                app_fixed = True
            
            # Solução ainda mais robusta: tenta simplesmente substituir toda a seção de importação do controlador
            # Esta é uma abordagem mais agressiva, mas pode resolver problemas sutis de importação
            if "controllers.main_controller" in app_content and not app_fixed:
                import re
                # Tenta encontrar e substituir o padrão de importação e registro com o padrão correto
                pattern = r"(?s)(# *Importar.*?controllers.*?main_controller.*?\n)(.*?)(app\.register_blueprint.*?\))"
                replacement = "\n# Importar e registrar controladores (corrigido automaticamente)\nfrom controllers.main_controller import main_bp\n\n# Registrar o blueprint\napp.register_blueprint(main_bp)"
                
                if re.search(pattern, app_content):
                    app_content = re.sub(pattern, replacement, app_content)
                    app_fixed = True
                else:
                    # Se não conseguiu encontrar o padrão específico, faz um fallback para uma abordagem mais simples
                    # Verifica se precisa adicionar a importação correta
                    if "from controllers.main_controller import main_bp" not in app_content:
                        # Encontra onde importações normalmente estariam
                        after_flask_import = app_content.find("from flask import") + 1
                        if after_flask_import > 0:
                            import_pos = app_content.find("\n\n", after_flask_import)
                            if import_pos > 0:
                                app_content = app_content[:import_pos] + "\n\n# Importação corrigida automaticamente\nfrom controllers.main_controller import main_bp" + app_content[import_pos:]
                                app_fixed = True
                    
                    # Verifica se precisa registrar o blueprint
                    if "app.register_blueprint(main_bp)" not in app_content:
                        app_pos = app_content.find("app = Flask(__name__)") + 1
                        if app_pos > 0:
                            insert_pos = app_content.find("\n\n", app_pos)
                            if insert_pos > 0:
                                app_content = app_content[:insert_pos] + "\n\n# Registro de blueprint corrigido automaticamente\napp.register_blueprint(main_bp)" + app_content[insert_pos:]
                                app_fixed = True
            
            # Se encontrou e corrigiu problemas, salva o arquivo
            if app_fixed:
                with open(app_path, 'w') as f:
                    f.write(app_content)
                    
        except Exception as e:
            print(f"Erro ao verificar app.py: {str(e)}")
    
    # Verificar e criar diretórios essenciais
    diretorios = [
        'controllers',
        'models',
        'templates',
        'static/css',
        'static/js',
        'utils',
        'instance'  # Adiciona o diretório instance para o banco de dados SQLite
    ]
    
    for diretorio in diretorios:
        dir_path = os.path.join(projeto_path, diretorio)
        os.makedirs(dir_path, exist_ok=True)
    
    # Adicionar os arquivos __init__.py
    init_py_content = "# Arquivo __init__.py para configurar o pacote"
    init_dirs = ['controllers', 'models', 'utils']
    
    # Cria estrutura especial para controllers/__init__.py para garantir importação correta
    controllers_init = os.path.join(projeto_path, 'controllers', '__init__.py')
    main_controller_path = os.path.join(projeto_path, 'controllers', 'main_controller.py')
    
    # Se o main_controller.py existe, configura o __init__.py para importá-lo corretamente
    if os.path.exists(main_controller_path):
        # Verificar o arquivo para detectar o nome do blueprint
        try:
            with open(main_controller_path, 'r') as f:
                controller_content = f.read()
            
            # Procura por padrões comuns de definição de blueprint
            import re
            bp_name = "main_bp"  # valor padrão
            bp_match = re.search(r'(\w+)\s*=\s*Blueprint\(', controller_content)
            if bp_match:
                bp_name = bp_match.group(1)
                
            # Cria ou substitui o __init__.py com a importação correta
            with open(controllers_init, 'w', encoding='utf-8') as f:
                f.write("# Arquivo __init__.py para o pacote controllers\n")
                f.write(f"# Configurado para importar {bp_name} automaticamente\n")
                f.write(f"# Para compatibilidade direta em importações simples\n")
                # IMPORTANTE: Em vez de importar de controllers.main_controller, colocamos a exportação direta
                f.write(f"from .main_controller import {bp_name}\n")
                
        except Exception as e:
            # Se falhar, usa a abordagem padrão
            if not os.path.exists(controllers_init):
                with open(controllers_init, 'w', encoding='utf-8') as f:
                    f.write(init_py_content)
    else:
        # Para os outros diretórios
        for init_dir in init_dirs:
            init_file_path = os.path.join(projeto_path, init_dir, '__init__.py')
            if not os.path.exists(init_file_path):
                with open(init_file_path, 'w', encoding='utf-8') as f:
                    f.write(init_py_content)
    
    # Verificar e criar os arquivos de template
    arquivos_template = {
        'app.py': '../utils/template_app.py',
        'controllers/main_controller.py': '../utils/template_controller.py',
        'models/database.py': '../utils/template_database.py',
        'models/exemplo.py': '../utils/template_exemplo.py'
    }
    
    for destino, origem in arquivos_template.items():
        destino_path = os.path.join(projeto_path, destino)
        origem_path = os.path.join(os.path.dirname(__file__), origem)
        
        # Se o arquivo não existir, copie do template
        if not os.path.exists(destino_path):
            with open(origem_path, 'r', encoding='utf-8') as f_origem:
                template_content = f_origem.read()
                
            # Certifique-se de que o diretório de destino existe
            os.makedirs(os.path.dirname(destino_path), exist_ok=True)
            
            with open(destino_path, 'w', encoding='utf-8') as f_destino:
                f_destino.write(template_content)
    
    # Verificar se há templates HTML básicos
    html_templates = {
        'templates/base.html': """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Projeto Flask{% endblock %}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
    </style>
    {% block head %}{% endblock %}
</head>
<body>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
    {% block scripts %}{% endblock %}
</body>
</html>
""",
        'templates/index.html': """{% extends "base.html" %}

{% block title %}Início{% endblock %}

{% block content %}
<h1>Bem-vindo ao Projeto Flask</h1>
<p>Este projeto foi reparado automaticamente pelo Dashboard.</p>
{% endblock %}
"""
    }
    
    for html_path, html_content in html_templates.items():
        file_path = os.path.join(projeto_path, html_path)
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
    
    # Verifica e repara problemas com banco de dados SQLite
    # 1. Cria um banco de dados vazio na pasta instance
    instance_dir = os.path.join(projeto_path, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    
    try:
        # Criar um arquivo de banco de dados SQLite vazio
        import sqlite3
        db_path = os.path.join(instance_dir, 'database.db')
        conn = sqlite3.connect(db_path)
        conn.close()
        
        # Verifica também se existe um app.db na raiz do projeto
        app_db_path = os.path.join(projeto_path, 'app.db')
        if not os.path.exists(app_db_path):
            conn = sqlite3.connect(app_db_path)
            conn.close()
            
        # Criar um arquivo especial para ajudar com importações no PythonAnywhere
        pathfix_file = os.path.join(projeto_path, 'pathfix.py')
        with open(pathfix_file, 'w') as f:
            f.write("# Arquivo criado automaticamente para ajudar com importações no PythonAnywhere\n")
            f.write("import os\n")
            f.write("import sys\n\n")
            f.write("# Adiciona o diretório atual ao sys.path\n")
            f.write("current_dir = os.path.abspath(os.path.dirname(__file__))\n")
            f.write("if current_dir not in sys.path:\n")
            f.write("    sys.path.insert(0, current_dir)\n")
            
        # Verificar o conteúdo do arquivo models/database.py
        database_path = os.path.join(projeto_path, 'models', 'database.py')
        app_path = os.path.join(projeto_path, 'app.py')
        
        if os.path.exists(database_path) and os.path.exists(app_path):
            with open(database_path, 'r') as f:
                database_content = f.read()
            
            with open(app_path, 'r') as f:
                app_content = f.read()
            
            # Se há referências ao SQLite mas não à pasta instance
            if 'sqlite:///' in database_content and 'instance' not in database_content:
                # Busca o template atualizado
                template_path = os.path.join(os.path.dirname(__file__), '../utils/template_database.py')
                with open(template_path, 'r') as f:
                    template_content = f.read()
                
                # Modifica para usar o caminho correto com instance
                corrected_content = template_content.replace(
                    "app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'app.db')",
                    "app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'instance', 'database.db')"
                )
                
                # Salva o arquivo corrigido
                with open(database_path, 'w') as f:
                    f.write(corrected_content)
    except Exception as e:
        print(f"Erro ao reparar banco de dados: {str(e)}")
    
    # Prepara mensagem para o usuário sobre o que foi reparado
    mensagem = "Projeto reparado com sucesso. "
    detalhes = []
    
    if app_fixed:
        detalhes.append("Corrigimos problemas de importação no app.py")
    
    if os.path.exists(controllers_init) and "from controllers.main_controller import" in open(controllers_init).read():
        detalhes.append("Configuramos os controladores para importação correta")
    
    if os.path.exists(os.path.join(projeto_path, 'instance')):
        detalhes.append("Configuramos o diretório instance para banco de dados")
        
    if detalhes:
        mensagem += "Melhorias: " + ", ".join(detalhes) + "."
    
    # Redirecionar para a página do projeto com mensagem de sucesso
    return redirect(url_for('dashboard.projeto', nome=nome))
