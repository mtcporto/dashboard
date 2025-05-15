import os

def listar_projetos(caminho_base):
    try:
        return [nome for nome in os.listdir(caminho_base)
                if os.path.isdir(os.path.join(caminho_base, nome))]
    except FileNotFoundError:
        return []
