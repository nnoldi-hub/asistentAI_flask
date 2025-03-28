from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"mesaj": "Salut, AI-ul tău Flask rulează pe Render.com!"})

@app.route('/ai', methods=['POST'])
def ai_reply():
    user_input = request.json.get('mesaj')
    # aici vei integra ulterior logica AI-ului
    return jsonify({"raspuns": f"AI-ul a primit mesajul: {user_input}"})

if __name__ == '__main__':
    app.run()
