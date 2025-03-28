
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import pickle, random
from datetime import datetime
import dateparser

app = Flask(__name__)
app.secret_key = 'secret_key_super_puternic'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai.db'
db = SQLAlchemy(app)

class Eveniment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mesaj_original = db.Column(db.String(500))
    data_ora = db.Column(db.DateTime)

with app.app_context():
    db.create_all()

model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
responses = pickle.load(open("responses.pkl", "rb"))

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/ai', methods=['POST'])
def ai_reply():
    user_input = request.json.get('mesaj')
    input_vec = vectorizer.transform([user_input])
    tag = model.predict(input_vec)[0]

    if tag == "adauga_eveniment":
        data_extrasa = dateparser.parse(user_input, languages=['ro'])
        if data_extrasa:
            eveniment = Eveniment(mesaj_original=user_input, data_ora=data_extrasa)
            db.session.add(eveniment)
            db.session.commit()
            raspuns = "Am salvat evenimentul pentru " + data_extrasa.strftime("%A, %d %B %Y ora %H:%M")
        else:
            raspuns = "Nu am putut înțelege data. Poți reformula?"
    else:
        raspuns = random.choice(responses[tag])

    return jsonify({"raspuns": raspuns})

@app.route('/verifica-evenimente')
def verifica_evenimente():
    acum = datetime.now()
    urmator = Eveniment.query.filter(Eveniment.data_ora > acum).order_by(Eveniment.data_ora).first()
    if urmator and (urmator.data_ora - acum).total_seconds() < 300:
        return jsonify({"mesaj": f"🔔 Reminder: {urmator.mesaj_original}"})
    return jsonify({})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        parola = request.form['parola']
        if username == 'admin' and parola == 'admin123':
            session['user'] = 'admin'
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', eroare="Date incorecte!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect(url_for('login'))
    evenimente = Eveniment.query.order_by(Eveniment.data_ora).all()
    return render_template('admin.html', evenimente=evenimente)

if __name__ == '__main__':
    app.run(debug=True)
