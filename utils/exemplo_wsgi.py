# Este é um arquivo WSGI de exemplo para configurar seus projetos Flask no PythonAnywhere
# Copie e modifique este arquivo para cada projeto

import sys
import os

# Adicione o caminho do projeto ao caminho de importação Python
path = '/home/devosflask/NOME_DO_PROJETO'  # <-- Substitua NOME_DO_PROJETO pelo nome real do seu projeto
if path not in sys.path:
    sys.path.insert(0, path)

# Importe sua aplicação Flask
from app import app as application  # Isso importa a variável 'app' do seu arquivo app.py como 'application'
