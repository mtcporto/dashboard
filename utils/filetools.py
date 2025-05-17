import os
import sys

def listar_pastas_projetos(caminho_base):
    """
    Lista todas as pastas de projetos válidos no caminho base,
    ignorando pastas de sistema e ocultas.
    """
    # Lista de pastas que devem ser ignoradas (pastas de sistema e ocultas)
    pastas_ignoradas = ['.virtualenvs', '.ipython', '.local', '.cache', '.ssh', '__pycache__']
    
    return [nome for nome in os.listdir(caminho_base)
            if os.path.isdir(os.path.join(caminho_base, nome)) and 
               not nome.startswith('.') and 
               nome not in pastas_ignoradas]

def verificar_projeto_flask(caminho_projeto):
    """
    Verifica se o diretório contém um projeto Flask válido
    verificando a existência de app.py ou algum blueprint.
    """
    # Verifica se há um app.py
    app_py_path = os.path.join(caminho_projeto, 'app.py')
    if os.path.exists(app_py_path):
        return True
        
    # Também verifica se há algum blueprint
    controllers_dir = os.path.join(caminho_projeto, 'controllers')
    if os.path.exists(controllers_dir) and os.path.isdir(controllers_dir):
        for arquivo in os.listdir(controllers_dir):
            if arquivo.endswith('.py'):
                return True
    
    return False

def importar_blueprint_projeto(nome_projeto, caminho_base):
    """
    Tenta importar e retornar o blueprint principal de um projeto Flask.
    Retorna o blueprint se encontrado, None caso contrário.
    """
    projeto_path = os.path.join(caminho_base, nome_projeto)
    
    # Verifica se é um projeto Flask
    if not verificar_projeto_flask(projeto_path):
        return None
    
    # Adiciona o caminho ao sys.path temporariamente
    sys.path.insert(0, os.path.dirname(projeto_path))
    
    try:
        # Tenta diferentes locais comuns para blueprints
        possíveis_módulos = [
            f'{nome_projeto}.controllers.main_controller',
            f'{nome_projeto}.controller',
            f'{nome_projeto}.app'
        ]
        
        for módulo_nome in possíveis_módulos:
            try:
                módulo = __import__(módulo_nome, fromlist=['main_bp', 'app_bp', 'blueprint', 'bp'])
                
                # Procura por blueprints comuns
                for bp_nome in ['main_bp', 'app_bp', 'blueprint', 'bp']:
                    if hasattr(módulo, bp_nome):
                        return getattr(módulo, bp_nome)
            except (ImportError, AttributeError):
                continue
                
    except Exception as e:
        print(f"Erro ao importar blueprint do projeto {nome_projeto}: {e}")
    finally:
        # Remove o caminho do projeto do sys.path
        if os.path.dirname(projeto_path) in sys.path:
            sys.path.remove(os.path.dirname(projeto_path))
    
    return None

# Atualizar listar_projetos para usar listar_pastas_projetos
listar_projetos = listar_pastas_projetos
