import os

def listar_pastas_projetos(caminho_base):
    pastas_relevantes = ['dashboard', 'mysite', 'teste']
    return [nome for nome in os.listdir(caminho_base)
            if nome in pastas_relevantes and os.path.isdir(os.path.join(caminho_base, nome))]

# Atualizar listar_projetos para usar listar_pastas_projetos
listar_projetos = listar_pastas_projetos
