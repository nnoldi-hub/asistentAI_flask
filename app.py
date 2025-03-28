
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ai', methods=['POST'])
def ai_reply():
    user_input = request.json.get('mesaj')
    raspuns = f"AI-ul a primit mesajul: {user_input}"
    return jsonify({"raspuns": raspuns})

if __name__ == '__main__':
    app.run(debug=True)
