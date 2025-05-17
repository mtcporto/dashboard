# Configuração do WSGI para executar o dashboard e projetos sob o mesmo domínio
# Caminho no PythonAnywhere: /var/www/devosflask_pythonanywhere_com_wsgi.py

import sys
import os

# Adicionar o caminho do dashboard ao caminho de importação Python
path = '/home/devosflask/dashboard'
if path not in sys.path:
    sys.path.insert(0, path)

# Importar a aplicação Flask do dashboard
from app import app as application

# Configuração para permitir o acesso aos subprojetos
# Define o diretório base onde estão todos os projetos
application.config['BASE_DIR'] = '/home/devosflask'

# Configurações adicionais para melhorar a performance e evitar vazamentos de memória
application.config['PROPAGATE_EXCEPTIONS'] = True  # Garantir que exceções sejam propagadas corretamente
application.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False  # Evitar vazamentos de contexto

# Certifique-se que todos os módulos necessários estão disponíveis no ambiente
# sys.path.append('/home/devosflask/.local/lib/python3.10/site-packages')
