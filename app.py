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
    from utils.filetools import listar_projetos, importar_blueprint_projeto
    
    projetos = listar_projetos(BASE_DIR)
    rotas_criadas = set()  # Conjunto para rastrear quais rotas já foram registradas
    
    for nome_projeto in projetos:
        # Ignora o dashboard que já está registrado
        if nome_projeto == 'dashboard' or nome_projeto == '__pycache__':
            continue
        
        projeto_path = os.path.join(BASE_DIR, nome_projeto)
        app_py_path = os.path.join(projeto_path, 'app.py')
        
        # Verifica se é uma pasta válida com arquivos Python
        if os.path.isdir(projeto_path):
            try:
                # Modo direto: Importa o app.py do projeto e verifica se tem blueprint
                if os.path.exists(app_py_path):
                    try:
                        # Adiciona o caminho do projeto ao sys.path
                        sys.path.insert(0, os.path.dirname(projeto_path))
                        
                        # Importa o módulo app.py usando importlib
                        spec = importlib.util.spec_from_file_location(f"{nome_projeto}.app", app_py_path)
                        projeto_app = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(projeto_app)
                        
                        # Verifica se há um Blueprint ou Flask app
                        found_blueprint = None
                        
                        # Procura por blueprints comuns
                        for attr_name in dir(projeto_app):
                            attr = getattr(projeto_app, attr_name)
                            if isinstance(attr, Blueprint):
                                found_blueprint = attr
                                break
                        
                        # Se encontrou um blueprint, registra com prefixo
                        if found_blueprint:
                            # Garante que não há duplicação de rotas
                            route_key = f"blueprint_{nome_projeto}"
                            if route_key not in rotas_criadas:
                                app.register_blueprint(found_blueprint, url_prefix=f'/{nome_projeto}')
                                rotas_criadas.add(route_key)
                                print(f"Registrado blueprint para projeto: {nome_projeto}")
                            continue
                    except Exception as e:
                        print(f"Erro ao importar app.py do projeto {nome_projeto}: {e}")
                    finally:
                        # Limpa o sys.path
                        if os.path.dirname(projeto_path) in sys.path:
                            sys.path.remove(os.path.dirname(projeto_path))
                
                # Modo alternativo: Cria rota de redirecionamento
                route_key = f"redirect_{nome_projeto}"
                if route_key not in rotas_criadas:
                    # Cria função de rota dinâmica para cada projeto
                    def create_project_route(projeto):
                        def project_route(path=""):
                            # Gera um número de porta aleatório entre 5000-5999 baseado no nome do projeto
                            # Isso é apenas para demonstração, em produção a porta seria fixa ou configurada
                            import hashlib
                            hash_obj = hashlib.md5(projeto.encode())
                            porta = 5000 + int(hash_obj.hexdigest(), 16) % 1000
                            
                            return render_template('projeto_redirect.html', 
                                                  nome=projeto, 
                                                  porta=porta)
                        return project_route
                    
                    # Registra rotas para o projeto
                    app.add_url_rule(f'/{nome_projeto}', 
                                    endpoint=f"project_{nome_projeto}", 
                                    view_func=create_project_route(nome_projeto))
                    
                    app.add_url_rule(f'/{nome_projeto}/<path:path>', 
                                    endpoint=f"project_path_{nome_projeto}", 
                                    view_func=create_project_route(nome_projeto))
                    
                    rotas_criadas.add(route_key)
                    print(f"Criada rota de redirecionamento para: {nome_projeto}")
                    
            except Exception as e:
                print(f"Erro ao registrar rotas para {nome_projeto}: {e}")

# Registrar os blueprints dos projetos
register_project_blueprints()

# Iniciar servidor se executado diretamente
if __name__ == '__main__':
    app.run(debug=True)
