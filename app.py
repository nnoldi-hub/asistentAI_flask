din flask import Flask, render_template, request, redirect, url_for, session, jsonify
din flask_sqlalchemy import SQLAlchemy
din werkzeug.security import generate_password_hash, check_password_hash
de la datetime import datetime, timedelta
din dateutil.parser import parse ca date_parse
import murat, aleatoriu, spațios

aplicație = Balon(__nume__)
app.secret_key = 'cheie_super_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_unificat.db'
db = SQLAlchemy(aplicație)

nlp = spacy.load("ro_core_news_sm")

clasa Utilizator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nume = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unic=True, nullable=False)
    parola = db.Column(db.String(200), nullable=False)

Eveniment de clasă (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utilizator.id'), nullable=True)
    mesaj = db.Column(db.String(500), nullable=False)
    data_ora = db.Column(db.DateTime, nullable=False)

cu app.app_context():
    db.create_all()

model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
răspunsuri = pickle.load(open("responses.pkl", "rb"))

def detecteaza_data(text):
    doc = nlp(text)
    azi = datetime.now()
    text = text.lower()

    dacă „mâine” în text:
        ora = [t.text pentru t în doc dacă t.like_num]
        returnează azi + timedelta(zile=1, ore=int(ora[0]) dacă sau altfel 10)

    dacă „poimâine” în text:
        ora = [t.text pentru t în doc dacă t.like_num]
        returnează azi + timedelta(zile=2, ore=int(ora[0]) dacă sau altfel 10)

    încerca:
        return date_parse(text, fuzzy=True, dayfirst=True)
    cu excepţia:
        return Niciunul

@app.route('/')
def index():
    dacă „admin” în sesiune:
        returnare redirecționare(url_for('admin'))
    dacă „user_id” în sesiune:
        evenimente = Eveniment.query.filter_by(user_id=session['user_id']).order_by(Eveniment.data_ora).all()
        return render_template("dashboard.html", evenimente=evenimente)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    dacă request.method == „POST”:
        nume = cerere.form['număr']
        email = request.form['email']
        parola = request.form['parola']
        parola_hash = generate_password_hash(parola)
        user = Utilizator(nume=nume, email=email, parola=parola_hash)
        db.session.add(utilizator)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    dacă request.method == „POST”:
        email = request.form['email']
        parola = request.form['parola']
        dacă e-mail == „admin” și parola == „admin123”:
            session['admin'] = Adevărat
            returnare redirecționare(url_for('admin'))
        utilizator = Utilizator.query.filter_by(email=email).first()
        if user și check_password_hash(user.parola, parola):
            session['user_id'] = user.id
            session['user_nume'] = user.nume
            returnează redirecționare(url_for('index'))
        altceva:
            return render_template("login.html", eroare="Data incorecte.")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/ai', methods=['POST'])
def ai():
    dacă „user_id” nu este în sesiune:
        return jsonify({"raspuns": "Trebuie să fii autentificat!"})
    mesaj = request.json.get('mesaj')
    input_vec = vectorizer.transform([mesaj])
    tag = model.predict(input_vec)[0]

    if tag == "adauga_eveniment":
        data_extrasa = detecteaza_data(mesaj)
        if data_extrasa:
            ev = Eveniment(user_id=session['user_id'], mesaj=mesaj, data_ora=data_extrasa)
            db.session.add(ev)
            db.session.commit()
            răspuns = f"✅ Eveniment salvat: {data_extrasa.strftime('%d-%m-%Y ora %H:%M')}"
        altceva:
            răspuns = "❌ Nu am putut înțelege data."
    altceva:
        răspuns = random.choice(responses[tag])
    return jsonify({"raspuns": raspuns})

@app.route('/admin')
def admin():
    dacă „admin” nu este în sesiune:
        return redirect(url_for('login'))
    utilizatori = Utilizator.query.all()
    evenimente = Eveniment.query.order_by(Eveniment.data_ora).all()
    return render_template("admin.html", utilizatori= persoane, evenimente=evenimente)
