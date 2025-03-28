from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai.db'
db = SQLAlchemy(app)

# Definirea structurii tabelului pentru conversații
class Conversatie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    intrebare = db.Column(db.String(500))
    raspuns = db.Column(db.String(500))

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ai', methods=['POST'])
def ai_reply():
    user_input = request.json.get('mesaj')

    # Căutare simplă a răspunsului în baza de date
    conv = Conversatie.query.filter(Conversatie.intrebare.ilike(f"%{user_input}%")).first()

    if conv:
        raspuns = conv.raspuns
    else:
        # Dacă nu găsim răspuns, salvăm întrebarea pentru a învăța ulterior
        raspuns = "Momentan nu știu, dar voi învăța."
        noua_conv = Conversatie(intrebare=user_input, raspuns=raspuns)
        db.session.add(noua_conv)
        db.session.commit()

    return jsonify({"raspuns": raspuns})

if __name__ == '__main__':
    app.run(debug=True)
