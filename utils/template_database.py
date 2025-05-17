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
        # SQLite - banco de dados local em arquivo na pasta instance (padrão do Flask)
        # Certifica-se de que a pasta instance existe
        instance_path = os.path.join(basedir, '..', 'instance')
        os.makedirs(instance_path, exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'database.db')
    elif database_type == 'mysql':
        # MySQL - substitua os valores por seus dados de conexão
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
    elif database_type == 'postgresql':
        # PostgreSQL - substitua os valores por seus dados de conexão
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/db_name'
    else:
        # Padrão para SQLite se tipo não reconhecido
        # Usa a pasta instance (padrão Flask) para o arquivo de banco de dados
        instance_path = os.path.join(basedir, '..', 'instance')
        os.makedirs(instance_path, exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'database.db')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar banco de dados
    db.init_app(app)
    
    # Criar todas as tabelas se não existirem
    with app.app_context():
        db.create_all()
    
    return db
