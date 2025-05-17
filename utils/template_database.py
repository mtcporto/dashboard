from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def setup_db(app, database_type='sqlite'):
    """
    Configura a conexão com o banco de dados
    
    Tipos suportados:
    - sqlite (padrão): SQLite local
    - mysql: MySQL
    - postgresql: PostgreSQL
    """
    
    # Diretório do projeto
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Configuração baseada no tipo de banco de dados
    if database_type == 'sqlite':
        # SQLite - banco de dados local em arquivo
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'app.db')
    elif database_type == 'mysql':
        # MySQL - substitua os valores por seus dados de conexão
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
    elif database_type == 'postgresql':
        # PostgreSQL - substitua os valores por seus dados de conexão
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/db_name'
    else:
        # Padrão para SQLite se tipo não reconhecido
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'app.db')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar banco de dados
    db.init_app(app)
    
    # Criar todas as tabelas se não existirem
    with app.app_context():
        db.create_all()
    
    return db
