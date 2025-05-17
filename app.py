import os
import sys
import importlib.util
from datetime import datetime
from flask import Flask, Blueprint, render_template, redirect, url_for, request, _request_ctx_stack

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
                        
                        # Define uma closure para servir os arquivos do projeto
                        def serve_project_root():
                            # Verifica se o projeto tem um app.py para ser executado diretamente
                            projeto_app_path = os.path.join(projeto_path, 'app.py')
                            if os.path.exists(projeto_app_path):
                                # Executar o projeto diretamente na mesma instância
                                return execute_project_app(projeto_path, projeto_app_path, nome_projeto, '/')
                            # Se não encontrou app.py, redireciona para gerenciamento no dashboard
                            else:
                                return redirect(url_for('dashboard.projeto', nome=nome_projeto))
                        
                        # Função para rotas com caminhos
                        def serve_project_path(path):
                            projeto_app_path = os.path.join(projeto_path, 'app.py')
                            if os.path.exists(projeto_app_path):
                                # Executa com o caminho específico
                                return execute_project_app(projeto_path, projeto_app_path, nome_projeto, '/' + path)
                            else:
                                return redirect(url_for('dashboard.projeto', nome=nome_projeto))
                        
                        # Função que executa o app do projeto
                        def execute_project_app(projeto_path, app_path, nome_projeto, path_override=None):
                            try:
                                # Guarda o caminho original
                                caminho_original = request.environ.get('PATH_INFO', '/')
                                
                                # Ajusta o caminho para o projeto
                                if path_override is not None:
                                    request.environ['PATH_INFO'] = path_override
                                
                                # Adiciona o caminho do projeto ao sys.path
                                sys.path.insert(0, projeto_path)
                                
                                # Importa o módulo app.py do projeto
                                spec = importlib.util.spec_from_file_location("project_app", app_path)
                                project_module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(project_module)
                                
                                # Obtém a aplicação Flask do módulo
                                if hasattr(project_module, 'app'):
                                    # Executa a requisição no contexto do projeto
                                    response = project_module.app.full_dispatch_request()
                                    return response
                                else:
                                    # Se não encontrar a aplicação Flask, exibe um erro
                                    return render_template('projeto_error.html', 
                                                          nome=nome_projeto, 
                                                          erro="O arquivo app.py não possui uma aplicação Flask válida"), 500
                            except Exception as e:
                                # Em caso de erro ao carregar o módulo, mostra o erro
                                return render_template('projeto_error.html', 
                                                      nome=nome_projeto, 
                                                      erro=f"Erro ao executar projeto: {str(e)}"), 500
                            finally:
                                # Restaura o caminho original
                                if path_override is not None:
                                    request.environ['PATH_INFO'] = caminho_original
                                # Limpa o sys.path
                                if projeto_path in sys.path:
                                    sys.path.remove(projeto_path)
                        
                        # Registramos as rotas no blueprint
                        bp.add_url_rule('/', 'index', serve_project_root)
                        bp.add_url_rule('/<path:path>', 'path', serve_project_path)
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
@app.route('/<nome_projeto>/', defaults={'path': ''})
@app.route('/<nome_projeto>/<path:path>')
def dynamic_project_route(nome_projeto, path):
    """Rota de fallback para qualquer projeto que ainda não tenha sido registrado"""
    # Verifica se o projeto existe na pasta de projetos
    from utils.filetools import listar_projetos
    projetos = listar_projetos(BASE_DIR)
    
    if nome_projeto in projetos:
        # Se o projeto existir, verifica se tem arquivo app.py
        projeto_path = os.path.join(BASE_DIR, nome_projeto)
        projeto_app_path = os.path.join(projeto_path, 'app.py')
        
        if os.path.exists(projeto_app_path):
            # Executar o projeto diretamente na mesma instância
            try:
                # Modifica o caminho da URL para simular a execução no diretório raiz do projeto
                # Isso permite que o Flask do projeto rode como se estivesse em sua própria raiz
                caminho_original = request.path
                if path:
                    # Preserva o PATH_INFO para rotas aninhadas (/nome_projeto/alguma/rota)
                    request.environ['PATH_INFO'] = '/' + path
                else:
                    # Define PATH_INFO para raiz do projeto (/nome_projeto/)
                    request.environ['PATH_INFO'] = '/'
                
                # Adiciona o caminho ao sys.path temporariamente
                sys.path.insert(0, projeto_path)
                
                # Importa o módulo app.py do projeto usando importlib
                spec = importlib.util.spec_from_file_location("project_app", projeto_app_path)
                project_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(project_module)
                
                # Obtém a aplicação Flask do módulo
                if hasattr(project_module, 'app'):
                    try:
                        # Função start_response para WSGI
                        def start_response(status, headers, exc_info=None):
                            return None
                            
                        # Redirecionar a solicitação para o app do projeto
                        response = project_module.app.full_dispatch_request()
                        return response
                    except Exception as e:
                        # Se houver erro na execução da requisição
                        return render_template('projeto_error.html', 
                                              nome=nome_projeto, 
                                              erro=f"Erro na execução do projeto: {str(e)}"), 500
                    finally:
                        # Restaura o PATH_INFO original
                        request.environ['PATH_INFO'] = caminho_original
                else:
                    # Se não encontrar a aplicação Flask, exibe um erro
                    return render_template('projeto_error.html', 
                                          nome=nome_projeto, 
                                          erro="O arquivo app.py não possui uma aplicação Flask válida"), 500
            except Exception as e:
                # Em caso de erro ao carregar o módulo, mostra o erro
                return render_template('projeto_error.html', 
                                      nome=nome_projeto, 
                                      erro=f"Erro ao executar projeto: {str(e)}"), 500
            finally:
                # Limpa o sys.path
                if projeto_path in sys.path:
                    sys.path.remove(projeto_path)
        else:
            # Se não tiver app.py, vai para gerenciamento
            return redirect(url_for('dashboard.projeto', nome=nome_projeto))
    else:
        # Se não existir, retorna uma página 404
        return render_template('404.html', projeto=nome_projeto), 404

# Iniciar servidor se executado diretamente
if __name__ == '__main__':
    app.run(debug=True)
