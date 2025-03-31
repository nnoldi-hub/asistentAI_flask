
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'cheie_super_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_multi.db'
db = SQLAlchemy(app)

class Utilizator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nume = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    parola = db.Column(db.String(200), nullable=False)

class Eveniment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utilizator.id'), nullable=False)
    mesaj = db.Column(db.String(500), nullable=False)
    data_ora = db.Column(db.DateTime, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if 'user_id' in session:
        evenimente = Eveniment.query.filter_by(user_id=session['user_id']).order_by(Eveniment.data_ora).all()
        return render_template('dashboard.html', evenimente=evenimente)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nume = request.form['nume']
        email = request.form['email']
        parola = request.form['parola']
        parola_hash = generate_password_hash(parola)
        user = Utilizator(nume=nume, email=email, parola=parola_hash)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        parola = request.form['parola']
        user = Utilizator.query.filter_by(email=email).first()
        if user and check_password_hash(user.parola, parola):
            session['user_id'] = user.id
            session['user_nume'] = user.nume
            return redirect(url_for('index'))
        else:
            return render_template('login.html', eroare="Date incorecte.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/adauga_eveniment', methods=['POST'])
def adauga_eveniment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    mesaj = request.form['mesaj']
    data_ora = datetime.strptime(request.form['data_ora'], "%Y-%m-%dT%H:%M")
    ev = Eveniment(user_id=session['user_id'], mesaj=mesaj, data_ora=data_ora)
    db.session.add(ev)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
