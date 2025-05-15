import os

def listar_pastas_projetos(caminho_base):
    # Lista de pastas que devem ser ignoradas (pastas de sistema e ocultas)
    pastas_ignoradas = ['.virtualenvs', '.ipython', '.local', '.cache', '.ssh', '__pycache__']
    
    return [nome for nome in os.listdir(caminho_base)
            if os.path.isdir(os.path.join(caminho_base, nome)) and 
               not nome.startswith('.') and 
               nome not in pastas_ignoradas]

# Atualizar listar_projetos para usar listar_pastas_projetos
listar_projetos = listar_pastas_projetos
