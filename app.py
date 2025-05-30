import os
import sys
import importlib.util
from datetime import datetime
from flask import Flask, Blueprint, render_template, redirect, url_for, request, _request_ctx_stack

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

# Rota de fallback para projetos
# Esta rota agora lida com a execução dinâmica dos projetos
@app.route('/<nome_projeto>/', defaults={'path': ''})
@app.route('/<nome_projeto>/<path:path>')
def dynamic_project_route(nome_projeto, path):
    """Rota de fallback para qualquer projeto"""
    from utils.filetools import listar_projetos
    projetos = listar_projetos(BASE_DIR)

    if nome_projeto in projetos:
        projeto_path = os.path.join(BASE_DIR, nome_projeto)
        projeto_app_path = os.path.join(projeto_path, 'app.py')

        if os.path.exists(projeto_app_path):
            try:
                # Salva os valores originais do ambiente
                original_path_info = request.environ.get('PATH_INFO', '/')
                original_script_name = request.environ.get('SCRIPT_NAME', '')

                # Calcula o novo PATH_INFO (caminho relativo dentro do projeto)
                # Ex: /nome_projeto/alguma/rota -> /alguma/rota
                # Certifica-se de que remove apenas o primeiro '/nome_projeto'
                # Usa startswith para ser mais preciso
                if original_path_info.startswith(f'/{nome_projeto}'):
                     new_path_info = original_path_info[len(f'/{nome_projeto}'):]
                     if not new_path_info.startswith('/'):
                          new_path_info = '/' + new_path_info
                else:
                     # Se por algum motivo a URL não começar com /nome_projeto, usa o caminho original
                     new_path_info = original_path_info


                # O SCRIPT_NAME deve ser o prefixo do projeto
                # Ex: / -> /nome_projeto
                # Ex: /dashboard -> /dashboard/nome_projeto
                new_script_name = original_script_name + f'/{nome_projeto}'

                # Armazena os originais para restaurar depois
                request.environ['ORIGINAL_PATH_INFO'] = original_path_info
                request.environ['ORIGINAL_SCRIPT_NAME'] = original_script_name

                # Define os novos valores para o app do projeto
                request.environ['PATH_INFO'] = new_path_info
                request.environ['SCRIPT_NAME'] = new_script_name

                # Adiciona o caminho do projeto ao sys.path temporariamente
                sys.path.insert(0, projeto_path)

                # Importa o módulo app.py do projeto
                spec = importlib.util.spec_from_file_location("project_app", projeto_app_path)
                project_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(project_module)

                # Obtém a aplicação Flask do módulo
                if hasattr(project_module, 'app'):
                    try:
                        # Salvar configuração original do app do projeto
                        original_project_config = {}
                        if hasattr(project_module.app, 'config'):
                            for key in project_module.app.config:
                                original_project_config[key] = project_module.app.config[key]

                        # Configurar o app do projeto para o ambiente atual
                        # O APPLICATION_ROOT deve ser o SCRIPT_NAME que definimos
                        project_module.app.config['APPLICATION_ROOT'] = new_script_name
                        project_module.app.config['DEBUG'] = False # Rodando sob o dashboard, debug deve ser tratado pelo dashboard

                        # Executa a requisição no contexto do projeto
                        # Usa o dispatcher do projeto
                        response = project_module.app.full_dispatch_request()

                        # Restaurar a configuração original do app do projeto
                        if hasattr(project_module.app, 'config'):
                            for key, value in original_project_config.items():
                                project_module.app.config[key] = value

                        return response

                    except ModuleNotFoundError as e:
                         # Capture ModuleNotFoundError e redirecione para a página de erro do dashboard
                         # Com informações para o usuário corrigir
                         error_message = f"Erro de módulo não encontrado no projeto '{nome_projeto}': {str(e)}. Verifique suas importações no app.py do projeto."
                         # Tente encontrar a linha do erro se possível
                         import traceback
                         tb_lines = traceback.format_exc().splitlines()
                         error_line = None
                         for line in reversed(tb_lines):
                             if f"File \"{projeto_app_path}\"" in line:
                                 match = re.search(r", line (\d+),", line)
                                 if match:
                                     error_line = match.group(1)
                                     break

                         if error_line:
                             return redirect(url_for('dashboard.editar_arquivo', nome=nome_projeto, path='app.py', errorLine=error_line))


                         # Fallback para a página de erro genérica do projeto se a edição não for aplicável ou falhar
                         return render_template('projeto_error.html',
                                                nome=nome_projeto,
                                                erro=error_message), 500


                    except Exception as e:
                        # Capture outras exceções e mostre na página de erro do dashboard
                        error_message = f"Erro na execução do projeto '{nome_projeto}': {str(e)}"

                        # Tente encontrar a linha do erro no traceback
                        import traceback
                        tb_lines = traceback.format_exc().splitlines()
                        error_line = None
                        error_file = 'app.py' # Assume que o erro está no app.py por padrão

                        # Busca pela linha do erro no traceback
                        for line in reversed(tb_lines):
                             if projeto_path in line: # Procura por linhas que contêm o caminho do projeto
                                 match = re.search(r"File \"(.*?)\", line (\d+),", line)
                                 if match:
                                     full_error_path = match.group(1)
                                     error_file = os.path.relpath(full_error_path, projeto_path)
                                     error_line = match.group(2)
                                     break

                        if error_line and error_file:
                            # Redireciona para a página de edição do arquivo com o erro destacado
                            return redirect(url_for('dashboard.editar_arquivo', nome=nome_projeto, path=error_file, errorLine=error_line))


                        # Fallback para a página de erro genérica do projeto
                        return render_template('projeto_error.html',
                                               nome=nome_projeto,
                                               erro=error_message), 500
                else:
                    # Se não encontrar a aplicação Flask no app.py do projeto
                    return render_template('projeto_error.html',
                                           nome=nome_projeto,
                                           erro=f"O arquivo app.py do projeto '{nome_projeto}' não possui uma instância de aplicação Flask válida (variável 'app')."), 500
            except Exception as e:
                # Erro ao carregar o módulo app.py do projeto
                error_message = f"Erro ao carregar o projeto '{nome_projeto}': {str(e)}"
                return render_template('projeto_error.html',
                                       nome=nome_projeto,
                                       erro=error_message), 500
            finally:
                # Limpa o sys.path
                if projeto_path in sys.path:
                    sys.path.remove(projeto_path)
                # Restaura os valores originais do request.environ
                if 'ORIGINAL_PATH_INFO' in request.environ:
                     request.environ['PATH_INFO'] = request.environ.pop('ORIGINAL_PATH_INFO')
                if 'ORIGINAL_SCRIPT_NAME' in request.environ:
                     request.environ['SCRIPT_NAME'] = request.environ.pop('ORIGINAL_SCRIPT_name')


        else:
            # Se não tiver app.py, vai para gerenciamento
            return redirect(url_for('dashboard.projeto', nome=nome_projeto))
    else:
        # Se não existir, retorna uma página 404
        return render_template('404.html', projeto=nome_projeto), 404

# Iniciar servidor se executado diretamente
if __name__ == '__main__':
    # Para WSGI, a aplicação é 'app'
    # Para desenvolvimento, usamos app.run()
    # Em produção com WSGI, o ponto de entrada será o objeto 'app'
    app.run(debug=True)
