
from flask import Flask, jsonify, request, render_template
import pickle, random

app = Flask(__name__)

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
    raspuns = random.choice(responses[tag])
    return jsonify({"raspuns": raspuns})

if __name__ == '__main__':
    app.run(debug=True)
