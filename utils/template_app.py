from flask import Flask, render_template, Blueprint
import os
import datetime
import sys

# Garantir que o diretório atual está no PYTHONPATH
current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Inicializar aplicação Flask com pasta instance configurada
app = Flask(__name__, instance_relative_config=True)

# Context processor para adicionar dados globais aos templates
@app.context_processor
def inject_context():
    return {
        'now': datetime.datetime.now()
    }

# Configuração do banco de dados
from models.database import setup_db
setup_db(app)

# Adicionando caminhos ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Importar e registrar controladores
import controllers # Isso executa controllers/__init__.py que deve expor main_bp

# Registrar o blueprint com prefixo vazio para funcionar como aplicação principal
# Isso permitirá acesso através de https://devosflask.pythonanywhere.com/nome_do_projeto
# controllers/__init__.py é responsável por importar e expor o blueprint correto (e.g., main_bp)
# O nome 'main_bp' é usado aqui porque é o nome padrão no template_controller.py e
# o que controllers/__init__.py irá exportar por padrão.
app.register_blueprint(controllers.main_bp)

# Registramos uma página para detectar o projeto no sistema de dashboard
@app.route('/dashboard_detect')
def dashboard_detect():
    return "Este é um projeto Flask válido"

if __name__ == '__main__':
    app.run(debug=True)
