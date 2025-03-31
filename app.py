from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dateutil.parser import parse as date_parse
import pickle, random, spacy

app = Flask(__name__)
app.secret_key = 'cheie_super_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_unificat.db'
db = SQLAlchemy(app)

nlp = spacy.load("ro_core_news_sm")

class Utilizator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nume = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    parola = db.Column(db.String(200), nullable=False)

class Conversatie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utilizator.id'))
    mesaj = db.Column(db.String(500))
    raspuns = db.Column(db.String(500))
    data_ora = db.Column(db.DateTime, default=datetime.now)

class Eveniment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utilizator.id'), nullable=True)
    mesaj = db.Column(db.String(500), nullable=False)
    data_ora = db.Column(db.DateTime, nullable=False)

with app.app_context():
    db.create_all()

model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
responses = pickle.load(open("responses.pkl", "rb"))

def detecteaza_data(text):
    doc = nlp(text)
    azi = datetime.now()
    text = text.lower()

    if "mâine" in text:
        ora = [t.text for t in doc if t.like_num]
        return azi + timedelta(days=1, hours=int(ora[0]) if ora else 10)

    if "poimâine" in text:
        ora = [t.text for t in doc if t.like_num]
        return azi + timedelta(days=2, hours=int(ora[0]) if ora else 10)

    try:
        return date_parse(text, fuzzy=True, dayfirst=True)
    except:
        return None


@app.route('/')
def index():
    if 'admin' in session:
        return redirect(url_for('admin'))
    if 'user_id' in session:
        evenimente = Eveniment.query.filter_by(user_id=session['user_id']).order_by(Eveniment.data_ora).all()
        conversatii = Conversatie.query.filter_by(user_id=session['user_id']).order_by(Conversatie.data_ora.desc()).limit(10).all()
        return render_template("dashboard.html", evenimente=evenimente, conversatii=conversatii)
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
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        parola = request.form['parola']
        if email == 'admin' and parola == 'admin123':
            session['admin'] = True
            return redirect(url_for('admin'))
        user = Utilizator.query.filter_by(email=email).first()
        if user and check_password_hash(user.parola, parola):
            session['user_id'] = user.id
            session['user_nume'] = user.nume
            return redirect(url_for('index'))
        else:
            return render_template("login.html", eroare="Date incorecte.")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/ai', methods=['POST'])
def ai():
    if 'user_id' not in session:
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
            raspuns = f"✅ Eveniment salvat: {data_extrasa.strftime('%d-%m-%Y ora %H:%M')}"
        else:
            raspuns = "❌ Nu am putut înțelege data."
    else:
        raspuns = random.choice(responses[tag])
    
    conv = Conversatie(user_id=session['user_id'], mesaj=mesaj, raspuns=raspuns)
    db.session.add(conv)
    db.session.commit()
    return jsonify({"raspuns": raspuns})

@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect(url_for('login'))
    utilizatori = Utilizator.query.all()
    evenimente = Eveniment.query.order_by(Eveniment.data_ora).all()
    return render_template("admin.html", utilizatori=utilizatori, evenimente=evenimente)

from flask import Response
import csv
from io import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

@app.route('/export_csv')
def export_csv():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Mesaj", "Raspuns", "Data/Ora"])
    convs = Conversatie.query.filter_by(user_id=session['user_id']).all()
    for c in convs:
        writer.writerow([c.mesaj, c.raspuns, c.data_ora])
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=istoric.csv"})

@app.route('/export_pdf')
def export_pdf():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    output = StringIO()
    pdf_path = "/tmp/conversatii.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    text_obj = c.beginText(40, 750)
    text_obj.setFont("Helvetica", 10)
    convs = Conversatie.query.filter_by(user_id=session['user_id']).all()
    for conv in convs:
        text_obj.textLine(f"{conv.data_ora} | {conv.mesaj} -> {conv.raspuns}")
    c.drawText(text_obj)
    c.showPage()
    c.save()
    with open(pdf_path, "rb") as pdf:
        return Response(pdf.read(), mimetype="application/pdf", headers={"Content-Disposition": "attachment;filename=istoric.pdf"})

@app.route('/admin/conversatii')
def admin_conversatii():
    if 'admin' not in session:
        return redirect(url_for('login'))
    convs = Conversatie.query.order_by(Conversatie.data_ora.desc()).limit(100).all()
    return render_template("admin_conversatii.html", conversatii=convs)


from sqlalchemy import func
@app.route('/admin/statistici')
def admin_statistici():
    if 'admin' not in session:
        return redirect(url_for('login'))
    statistici = db.session.query(
        func.date(Conversatie.data_ora),
        func.count(Conversatie.id)
    ).group_by(func.date(Conversatie.data_ora)).all()
    labels = [str(row[0]) for row in statistici]
    values = [row[1] for row in statistici]
    return render_template("admin_statistici.html", labels=labels, values=values)


@app.route('/export_evenimente_csv')
def export_evenimente_csv():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Data/Ora", "Descriere"])
    evenimente = Eveniment.query.filter_by(user_id=session['user_id']).order_by(Eveniment.data_ora).all()
    for ev in evenimente:
        writer.writerow([ev.data_ora.strftime('%Y-%m-%d %H:%M'), ev.mesaj])
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=calendar.csv"})

@app.route('/export_evenimente_pdf')
def export_evenimente_pdf():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    pdf_path = "/tmp/calendar.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    text = c.beginText(40, 750)
    text.setFont("Helvetica", 10)
    evenimente = Eveniment.query.filter_by(user_id=session['user_id']).order_by(Eveniment.data_ora).all()
    for ev in evenimente:
        text.textLine(f"{ev.data_ora.strftime('%Y-%m-%d %H:%M')} - {ev.mesaj}")
    c.drawText(text)
    c.showPage()
    c.save()
    with open(pdf_path, "rb") as pdf:
        return Response(pdf.read(), mimetype="application/pdf", headers={"Content-Disposition": "attachment;filename=calendar.pdf"})