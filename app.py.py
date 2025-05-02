from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave-secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Tipos de usuário
TIPOS_USUARIO = ['vendedor', 'caixa', 'estoque']

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    login = db.Column(db.String(50), unique=True)
    senha = db.Column(db.String(50))
    cargo = db.Column(db.String(20))

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_venda = db.Column(db.String(20))
    prioridade = db.Column(db.Integer)
    vendedor = db.Column(db.String(100))
    data_criacao = db.Column(db.DateTime, default=datetime.now)

    nf_pronta = db.Column(db.Boolean, default=False)
    guia_paga = db.Column(db.Boolean, default=False)
    data_financeiro = db.Column(db.DateTime, nullable=True)

    separado = db.Column(db.Boolean, default=False)
    data_estoque = db.Column(db.DateTime, nullable=True)

    def finalizado(self):
        return self.nf_pronta and self.guia_paga and self.separado

@app.before_first_request
def criar_tabelas():
    db.create_all()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(login=login, senha=senha).first()
        if usuario:
            session['usuario_id'] = usuario.id
            session['cargo'] = usuario.cargo
            session['nome'] = usuario.nome
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', erro='Login inválido')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    pedidos = Pedido.query.all()
    abertos = sorted([p for p in pedidos if not p.finalizado()], key=lambda x: x.prioridade)
    finalizados = [p for p in pedidos if p.finalizado()]
    return render_template('dashboard.html', abertos=abertos, finalizados=finalizados)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if session.get('cargo') != 'vendedor':
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        numero = request.form['numero']
        prioridade = int(request.form['prioridade'])
        pedido = Pedido(numero_venda=numero, prioridade=prioridade, vendedor=session['nome'])
        db.session.add(pedido)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('cadastro.html')

@app.route('/atualizar/<int:pedido_id>', methods=['POST'])
def atualizar(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    if session.get('cargo') == 'caixa':
        pedido.nf_pronta = 'nf_pronta' in request.form
        pedido.guia_paga = 'guia_paga' in request.form
        pedido.data_financeiro = datetime.now()
    elif session.get('cargo') == 'estoque':
        pedido.separado = 'separado' in request.form
        pedido.data_estoque = datetime.now()
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
