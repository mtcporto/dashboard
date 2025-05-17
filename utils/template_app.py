from flask import Flask, render_template, Blueprint
import os
import datetime

app = Flask(__name__)

# Context processor para adicionar dados globais aos templates
@app.context_processor
def inject_context():
    return {
        'now': datetime.datetime.now()
    }

# Configuração do banco de dados
from models.database import setup_db
setup_db(app)

# Importar e registrar controladores
from controllers.main_controller import main_bp

# Registrar o blueprint com prefixo vazio para funcionar como aplicação principal
# Isso permitirá acesso através de https://devosflask.pythonanywhere.com/nome_do_projeto
app.register_blueprint(main_bp, url_prefix='')

if __name__ == '__main__':
    app.run(debug=True)
