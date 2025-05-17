from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models.database import db
from models.exemplo import Exemplo

# Blueprint que poderá ser acessado diretamente na URL
# Nota: Ao acessar pelo dashboard, o blueprint será registrado com prefixo /nome_projeto
main_bp = Blueprint('main_bp', __name__, url_prefix='')

@main_bp.route('/')
def index():
    """Página inicial do projeto"""
    return render_template('index.html')

@main_bp.route('/sobre')
def sobre():
    """Página de informações sobre o projeto"""
    return render_template('sobre.html')

@main_bp.route('/api/exemplos', methods=['GET'])
def listar_exemplos():
    """API para listar exemplos"""
    exemplos = Exemplo.query.all()
    return jsonify({
        'success': True,
        'exemplos': [exemplo.format() for exemplo in exemplos]
    })

@main_bp.route('/api/exemplos', methods=['POST'])
def criar_exemplo():
    """API para criar um novo exemplo"""
    try:
        data = request.get_json()
        titulo = data.get('titulo')
        descricao = data.get('descricao', '')
        
        novo_exemplo = Exemplo(titulo=titulo, descricao=descricao)
        db.session.add(novo_exemplo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'exemplo': novo_exemplo.format()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
