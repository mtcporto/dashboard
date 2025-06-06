import os
import sys
import importlib.util
from datetime import datetime
from flask import Flask, Blueprint, render_template, redirect, url_for, request, _request_ctx_stack
import os # Certifique-se de que os está importado

# Define base directory as the parent of the dashboard directory
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
                                    try:
                                        # Salvar configuração original do app
                                        original_config = {}
                                        if hasattr(project_module.app, 'config'):
                                            for key in project_module.app.config:
                                                original_config[key] = project_module.app.config[key]
                                        
                                        # Configurar o app do projeto para o ambiente atual
                                        project_module.app.config['APPLICATION_ROOT'] = f'/{nome_projeto}'
                                        project_module.app.config['DEBUG'] = False
                                        
                                        # Executa a requisição no contexto do projeto
                                        response = project_module.app.full_dispatch_request()
                                        
                                        # Restaurar a configuração original
                                        if hasattr(project_module.app, 'config'):
                                            for key, value in original_config.items():
                                                project_module.app.config[key] = value
                                        
                                        return response
                                    except ModuleNotFoundError as e:
                                        # Se o erro for de módulo não encontrado, mostramos informações de como corrigir
                                        if "controllers.main_controller" in str(e):
                                            # Criar pasta controllers se não existir
                                            controllers_dir = os.path.join(projeto_path, 'controllers')
                                            os.makedirs(controllers_dir, exist_ok=True)
                                            
                                            # Verificar se o PYTHONPATH está correto
                                            # Verificar app.py para possíveis problemas de importação
                                            app_path = os.path.join(projeto_path, 'app.py')
                                            app_fixed = False
                                            
                                            if os.path.exists(app_path):
                                                try:
                                                    with open(app_path, 'r') as f:
                                                        app_content = f.read()
                                                        
                                                    # Verifica padrões problemáticos de importação
                                                    if "from controllers import main_controller" in app_content:
                                                        # Corrige para importação correta
                                                        app_content = app_content.replace(
                                                            "from controllers import main_controller", 
                                                            "from controllers.main_controller import main_bp")
                                                        app_fixed = True
                                                    elif "import controllers.main_controller" in app_content and "main_bp" not in app_content:
                                                        # Adiciona referência ao blueprint
                                                        app_content = app_content.replace(
                                                            "import controllers.main_controller", 
                                                            "from controllers.main_controller import main_bp")
                                                        app_fixed = True
                                                        
                                                    # Se encontrou e corrigiu problemas, salva o arquivo
                                                    if app_fixed:
                                                        with open(app_path, 'w') as f:
                                                            f.write(app_content)
                                                except Exception:
                                                    pass
                                            
                                            # Primeiro verifica se existe controller.py em vez de main_controller.py
                                            controller_file_path = os.path.join(controllers_dir, 'controller.py')
                                            if os.path.exists(controller_file_path):
                                                # Cria compatibilidade entre controller.py e main_controller.py
                                                try:
                                                    with open(controller_file_path, 'r') as f:
                                                        controller_content = f.read()
                                                    
                                                    # Criar main_controller.py
                                                    main_controller_path = os.path.join(controllers_dir, 'main_controller.py')
                                                    with open(main_controller_path, 'w') as f:
                                                        f.write(controller_content)
                                                    
                                                    # Criar __init__.py se não existir
                                                    init_file = os.path.join(controllers_dir, '__init__.py')
                                                    if not os.path.exists(init_file):
                                                        with open(init_file, 'w') as f:
                                                            f.write("# Arquivo de compatibilidade\n")
                                                            f.write("from controllers.main_controller import *\n")
                                                    
                                                    msg = "Encontramos um controller.py e criamos main_controller.py para compatibilidade."
                                                    if app_fixed:
                                                        msg += " Também corrigimos problemas de importação no app.py."
                                                    
                                                    return render_template('projeto_error.html', 
                                                                nome=nome_projeto, 
                                                                erro=f"{msg} Por favor, tente novamente."), 500
                                                except Exception as copy_error:
                                                    pass  # Se falhar, continua para o código abaixo
                                            
                                            # Se não existe controller.py ou falhou ao copiar, usa o template
                                            # CORRIGIDO: Caminho para o template_controller.py
                                            template_controller_path = os.path.join(os.path.dirname(__file__), 
                                                                                'utils/template_controller.py')
                                            
                                            if os.path.exists(template_controller_path):
                                                with open(template_controller_path, 'r') as f:
                                                    controller_content = f.read()
                                                
                                                # Criar o arquivo main_controller.py
                                                controller_file = os.path.join(controllers_dir, 'main_controller.py')
                                                with open(controller_file, 'w') as f:
                                                    f.write(controller_content)
                                                
                                                # Criar __init__.py na pasta controllers com lógica robusta
                                                init_file = os.path.join(controllers_dir, '__init__.py')
                                                
                                                blueprint_name = "main_bp" # Default
                                                # Tenta detectar o nome do blueprint do main_controller.py (template ou copiado)
                                                try:
                                                    import re
                                                    bp_match = re.search(r'(\w+)\s*=\s*Blueprint\(', controller_content)
                                                    if bp_match:
                                                        blueprint_name = bp_match.group(1)
                                                except Exception:
                                                    pass # Mantém o padrão se a detecção falhar

                                                with open(init_file, 'w') as f:
                                                    f.write("# Arquivo __init__.py para o pacote controllers\n")
                                                    f.write("# Configuração automática para garantir importações corretas\n")
                                                    f.write("import os\n")
                                                    f.write("import sys\n\n")
                                                    f.write("# Garantir que o diretório pai (raiz do projeto) está no PYTHONPATH\n")
                                                    f.write("_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))\n")
                                                    f.write("if _project_root not in sys.path:\n")
                                                    f.write("    sys.path.insert(0, _project_root)\n\n")
                                                    f.write(f"# Exportar {blueprint_name} diretamente\n")
                                                    f.write(f"from .main_controller import {blueprint_name}\n")
                                                
                                                return render_template('projeto_error.html', 
                                                                nome=nome_projeto, 
                                                                erro=f"Corrigimos automaticamente o erro '{str(e)}'. Por favor, tente novamente."), 500
                                        
                                        # Para outros erros de módulos não encontrados
                                        return render_template('projeto_error.html', 
                                                          nome=nome_projeto, 
                                                          erro=f"Erro de módulo não encontrado: {str(e)}. Verifique se todos os arquivos necessários foram criados."), 500
                                else:
                                    # Se não encontrar a aplicação Flask, exibe um erro
                                    return render_template('projeto_error.html', 
                                                          nome=nome_projeto, 
                                                          erro="O arquivo app.py não possui uma aplicação Flask válida"), 500
                            except Exception as e:
                                # Em caso de erro ao carregar o módulo, mostra o erro
                                error_str = str(e) # Definir error_str
                                
                                # Verifica se é um erro de SQLite de arquivo de banco de dados
                                if "sqlite3.OperationalError" in error_str and "unable to open database file" in error_str:
                                    # Criar o diretório instance para o banco de dados se não existir
                                    instance_dir = os.path.join(projeto_path, 'instance') # Definir instance_dir
                                    os.makedirs(instance_dir, exist_ok=True)
                                    
                                    # Criar um arquivo de banco de dados vazio
                                    try:
                                        import sqlite3 # Importar sqlite3
                                        db_path = os.path.join(instance_dir, 'database.db')
                                        conn = sqlite3.connect(db_path)
                                        conn.close()
                                    except:
                                        pass  # Se falhar ao criar o DB, continuamos mesmo assim
                                    
                                    # Verificar configuração do SQLAlchemy no app.py
                                    try:
                                        with open(app_path, 'r') as f:
                                            app_content = f.read()
                                            
                                        # Se a configuração do banco de dados parece estar usando um caminho relativo
                                        if "sqlite:///" in app_content and "instance_path" not in app_content:
                                            return render_template('projeto_error.html',
                                                                 nome=nome_projeto,
                                                                 erro=f"Erro de banco de dados SQLite: {error_str}. Criamos a pasta 'instance' com um banco de dados vazio. Use um caminho absoluto para o SQLite ou configure instance_path."), 500
                                    except:
                                        pass
                                
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
                        
                        # Salvar configuração original do app
                        original_config = {}
                        if hasattr(project_module.app, 'config'):
                            for key in project_module.app.config:
                                original_config[key] = project_module.app.config[key]
                                
                        # Configurar o app do projeto para o ambiente atual
                        project_module.app.config['APPLICATION_ROOT'] = f'/{nome_projeto}'
                        project_module.app.config['DEBUG'] = False
                        
                        # Redirecionar a solicitação para o app do projeto
                        response = project_module.app.full_dispatch_request()
                        
                        # Restaurar a configuração original
                        if hasattr(project_module.app, 'config'):
                            for key, value in original_config.items():
                                project_module.app.config[key] = value
                                
                        return response
                    except ModuleNotFoundError as e:
                        # Se o erro for de módulo não encontrado, mostramos informações de como corrigir
                        if "controllers.main_controller" in str(e):
                            # Criar pasta controllers se não existir
                            controllers_dir = os.path.join(projeto_path, 'controllers')
                            os.makedirs(controllers_dir, exist_ok=True)
                            
                            # Criar pasta models se não existir (para projetos que usam SQLAlchemy)
                            models_dir = os.path.join(projeto_path, 'models')
                            os.makedirs(models_dir, exist_ok=True)
                            
                            # Criar __init__.py na pasta models para evitar erros de importação
                            models_init = os.path.join(models_dir, '__init__.py')
                            if not os.path.exists(models_init):
                                with open(models_init, 'w') as f:
                                    f.write("# Arquivo __init__.py para o pacote models\n")
                            
                            # Primeiro verifica se existe um controller.py (nome comum que pode estar sendo usado)
                            existing_controller_path = os.path.join(controllers_dir, 'controller.py')
                            
                            if os.path.exists(existing_controller_path):
                                # Se existe um controller.py, vamos renomeá-lo para main_controller.py
                                # e ajustá-lo para usar o nome correto
                                try:
                                    with open(existing_controller_path, 'r') as f:
                                        existing_content = f.read()
                                    
                                    # Criar novo arquivo com o nome correto
                                    controller_file = os.path.join(controllers_dir, 'main_controller.py')
                                    with open(controller_file, 'w') as f:
                                        f.write(existing_content)
                                        
                                    # Manter o original para compatibilidade
                                    
                                    # Criar __init__.py na pasta controllers se não existir
                                    init_file = os.path.join(controllers_dir, '__init__.py')
                                    if not os.path.exists(init_file):
                                        # Tenta identificar o nome do blueprint no controller original
                                        blueprint_name = "main_bp"  # Valor padrão
                                        try:
                                            with open(existing_controller_path, 'r') as f:
                                                content = f.read()
                                                # Procura por padrões comuns de definição de blueprint
                                                import re
                                                bp_match = re.search(r'(\w+)\s*=\s*Blueprint\(', content)
                                                if bp_match:
                                                    blueprint_name = bp_match.group(1)
                                        except:
                                            # Se falhar na detecção, usa o padrão
                                            pass
                                            
                                        with open(init_file, 'w') as f:
                                            f.write("# Arquivo __init__.py para o pacote controllers\n")
                                            f.write("# Importação para compatibilidade\n")
                                            f.write(f"from controllers.main_controller import {blueprint_name}\n")
                                    
                                    return render_template('projeto_error.html', 
                                                      nome=nome_projeto, 
                                                      erro=f"Encontramos um controller.py e criamos main_controller.py para compatibilidade. Por favor, tente novamente."), 500
                                except Exception as copy_error:
                                    return render_template('projeto_error.html', 
                                                      nome=nome_projeto, 
                                                      erro=f"Erro ao copiar controller.py para main_controller.py: {str(copy_error)}"), 500
                            else:
                                # Verificar se existe o template do controller
                                template_controller_path = os.path.join(os.path.dirname(__file__), 
                                                                    'utils/template_controller.py')
                                
                                if os.path.exists(template_controller_path):
                                    with open(template_controller_path, 'r') as f:
                                        controller_content = f.read()
                                    
                                    # Criar o arquivo main_controller.py
                                    controller_file = os.path.join(controllers_dir, 'main_controller.py')
                                    with open(controller_file, 'w') as f:
                                        f.write(controller_content)
                                    
                                                        # Criar __init__.py na pasta controllers
                                    init_file = os.path.join(controllers_dir, '__init__.py')
                                    with open(init_file, 'w') as f:
                                        f.write("# Arquivo __init__.py para o pacote controllers\n")
                                        f.write("# Configuração automática para garantir importações corretas\n")
                                        f.write("import os\n")
                                        f.write("import sys\n\n")
                                        f.write("# Garantir que o diretório pai está no PYTHONPATH\n")
                                        f.write("_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))\n")
                                        f.write("if _parent_dir not in sys.path:\n")
                                        f.write("    sys.path.insert(0, _parent_dir)\n\n")
                                        f.write("# Exportar main_bp diretamente para permitir import from controllers\n")
                                        f.write("from .main_controller import main_bp\n")
                                    
                                    return render_template('projeto_error.html', 
                                                      nome=nome_projeto, 
                                                      erro=f"Corrigimos automaticamente o erro '{str(e)}'. Por favor, tente novamente."), 500
                        
                        # Para outros erros de módulos não encontrados
                        return render_template('projeto_error.html', 
                                              nome=nome_projeto, 
                                              erro=f"Erro de módulo não encontrado: {str(e)}. Verifique se todos os arquivos necessários foram criados."), 500
                    except Exception as e:
                        # Se houver erro na execução da requisição
                        error_str = str(e)
                        
                        # Verifica se é um erro de SQLite de arquivo de banco de dados
                        if "sqlite3.OperationalError" in error_str and "unable to open database file" in error_str:
                            # Criar o diretório instance para o banco de dados se não existir
                            instance_dir = os.path.join(projeto_path, 'instance')
                            os.makedirs(instance_dir, exist_ok=True)
                            
                            # Criar um arquivo de banco de dados vazio
                            try:
                                import sqlite3
                                db_path = os.path.join(instance_dir, 'database.db')
                                conn = sqlite3.connect(db_path)
                                conn.close()
                            except:
                                pass  # Se falhar ao criar o DB, continuamos mesmo assim
                            
                            # Verificar configuração do SQLAlchemy no app.py
                            try:
                                with open(projeto_app_path, 'r') as f:
                                    app_content = f.read()
                                    
                                # Se a configuração do banco de dados parece estar usando um caminho relativo
                                if "sqlite:///" in app_content and "instance_path" not in app_content:
                                    return render_template('projeto_error.html',
                                                         nome=nome_projeto,
                                                         erro=f"Erro de banco de dados SQLite: {error_str}. Criamos a pasta 'instance' com um banco de dados vazio. Use um caminho absoluto para o SQLite ou configure instance_path."), 500
                            except:
                                pass
                                
                        # Para outros erros na execução da requisição
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
