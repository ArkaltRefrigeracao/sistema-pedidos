from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SECRET_KEY'] = 'minha-chave-secreta'

db = SQLAlchemy(app)

# Modelos
class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='aberto')
    prioridade = db.Column(db.Integer, default=1)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    responsavel = db.Column(db.String(50))
    hora_ultima_acao = db.Column(db.DateTime)

# Roda uma vez antes da primeira requisição
@app.before_request
def criar_banco_uma_vez():
    if not hasattr(app, 'banco_inicializado'):
        db.create_all()
        app.banco_inicializado = True

# Rotas
@app.route('/')
def index():
    pedidos = Pedido.query.filter_by(status='aberto').order_by(Pedido.prioridade.desc()).all()
    return render_template('index.html', pedidos=pedidos)

@app.route('/criar', methods=['POST'])
def criar():
    descricao = request.form['descricao']
    prioridade = request.form.get('prioridade', 1)
    novo_pedido = Pedido(descricao=descricao, prioridade=int(prioridade))
    db.session.add(novo_pedido)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/atualizar/<int:id>', methods=['POST'])
def atualizar(id):
    pedido = Pedido.query.get_or_404(id)
    novo_status = request.form.get('status', 'aberto')
    pedido.status = novo_status
    pedido.hora_ultima_acao = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
