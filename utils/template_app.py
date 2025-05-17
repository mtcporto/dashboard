from flask import Flask, render_template, Blueprint
import os

app = Flask(__name__)

# Configuração do banco de dados
from models.database import setup_db
setup_db(app)

# Importar e registrar controladores
from controllers.main_controller import main_bp

# Se registrado como Blueprint, você pode acessar pela URL principal do site
# Ex: https://devosflask.pythonanywhere.com/nome_do_projeto
app.register_blueprint(main_bp)

# Se preferir acessar diretamente na raiz, descomente esta linha:
# app.register_blueprint(main_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)
