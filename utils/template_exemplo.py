from models.database import db
from datetime import datetime

class Exemplo(db.Model):
    __tablename__ = 'exemplos'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, titulo, descricao):
        self.titulo = titulo
        self.descricao = descricao
    
    def format(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'data_criacao': self.data_criacao.strftime('%Y-%m-%d %H:%M:%S')
        }
