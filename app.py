import os
import sys
import importlib.util
from datetime import datetime
from flask import Flask, Blueprint, render_template, redirect, url_for, request

# Define base directory as parent of dashboard dir
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
app = Flask(__name__)
app.config['BASE_DIR'] = BASE_DIR

# Adicionar data atual e objeto request ao contexto de todos os templates
@app.context_processor
def inject_context():
    return {
        'now': datetime.now(),
        'request': request
    }

# Register dashboard blueprint no prefixo /dashboard
from controllers.dashboard import dashboard_bp
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

# Rota raiz para redirecionar para o dashboard
@app.route('/')
def index():
    return redirect(url_for('dashboard.index'))

# Função para registrar projetos dinamicamente
def register_project_blueprints():
    """Registra blueprints para todos os projetos na pasta de projetos"""
    from utils.filetools import listar_projetos
    
    projetos = listar_projetos(BASE_DIR)
    rotas_criadas = set()  # Conjunto para rastrear quais rotas já foram registradas
    
    for nome_projeto in projetos:
        # Ignora o dashboard que já está registrado e outros diretórios especiais
        if nome_projeto == 'dashboard' or nome_projeto == '__pycache__' or nome_projeto.startswith('.'):
            continue
        
        projeto_path = os.path.join(BASE_DIR, nome_projeto)
        
        # Verifica se é uma pasta válida
        if os.path.isdir(projeto_path):
            try:
                # Cria um blueprint simples para o projeto
                route_key = f"project_{nome_projeto}"
                if route_key not in rotas_criadas:
                    # Criamos uma função closure para preservar o nome do projeto
                    # Usamos uma função factory para criar blueprints
                    # com escopo adequado para cada projeto
                    def create_project_blueprint(nome_projeto):
                        # Nome único para evitar colisões
                        blueprint_name = f'project_{nome_projeto}'
                        bp = Blueprint(blueprint_name, __name__, url_prefix=f'/{nome_projeto}')
                        
                        # Definimos uma função closure para capturar o nome do projeto
                        def index_route():
                            return redirect(url_for('dashboard.projeto', nome=nome_projeto))
                        
                        # Registramos a rota no blueprint
                        bp.add_url_rule('/', 'index', index_route)
                        return bp
                    
                    # Criamos o blueprint com o nome do projeto
                    bp = create_project_blueprint(nome_projeto)
                    app.register_blueprint(bp)
                    
                    rotas_criadas.add(route_key)
                    print(f"Registrado blueprint para projeto: {nome_projeto}")
                    
            except Exception as e:
                print(f"Erro ao registrar blueprint para {nome_projeto}: {e}")

# Registrar os blueprints dos projetos
register_project_blueprints()

# Rota de fallback para projetos não registrados explicitamente
@app.route('/<nome_projeto>/')
@app.route('/<nome_projeto>')
def dynamic_project_route(nome_projeto):
    """Rota de fallback para qualquer projeto que ainda não tenha sido registrado"""
    # Verifica se o projeto existe na pasta de projetos
    from utils.filetools import listar_projetos
    projetos = listar_projetos(BASE_DIR)
    
    if nome_projeto in projetos:
        # Se o projeto existir, redireciona para a página do projeto
        return redirect(url_for('dashboard.projeto', nome=nome_projeto))
    else:
        # Se não existir, retorna uma página 404
        return render_template('404.html', projeto=nome_projeto), 404

# Iniciar servidor se executado diretamente
if __name__ == '__main__':
    app.run(debug=True)
