from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OpenAI.api_key = "YOUR_API_KEY"

app = Flask(__name__)
CORS(app)

# ---------------- DATABASE ---------------- #

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT,
        response TEXT,
        timestamp TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS diseases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        symptoms TEXT,
        precautions TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

# ---------------- ADD DATA ---------------- #

def add_disease_data():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    data = [
        ("Dengue","fever, headache, joint pain","avoid mosquitoes"),
        ("Malaria","fever, chills, sweating","use nets"),
        ("COVID","fever, cough","mask, isolate"),
        ("Flu","cold, fever","rest, fluids"),
        ("Diabetes","fatigue, thirst","control sugar"),
        ("Asthma","breathing issue","avoid dust")
    ]

    c.executemany("INSERT INTO diseases (name, symptoms, precautions) VALUES (?,?,?)", data)

    conn.commit()
    conn.close()

add_disease_data()

# ---------------- RESPONSE ---------------- #

def get_health_response(msg):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT name, symptoms, precautions FROM diseases")
    diseases = c.fetchall()

    for d in diseases:
        name, symptoms, precautions = d
        for s in symptoms.split(","):
            if s.strip() in msg.lower():
                return f"""
 Possible Disease: {name}

 Symptoms: {symptoms}

 Precautions: {precautions}

⚠️ Consult a doctor.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are a helpful medical assistant."},
                {"role":"user","content":msg}
            ]
        )
        return response['choices'][0]['message']['content']

    except:
        return "Please explain symptoms clearly."

# ---------------- ROUTES ---------------- #

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data['message']

    response = get_health_response(message)

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("INSERT INTO chats (message, response, timestamp) VALUES (?,?,?)",
              (message, response, str(datetime.datetime.now())))

    conn.commit()
    conn.close()

    return jsonify({"response": response})

# ADMIN PANEL DATA
@app.route('/admin', methods=['GET'])
def admin():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM chats")
    data = c.fetchall()
    conn.close()
    return jsonify(data)

# ---------------- RUN ---------------- #

if __name__ == '__main__':
    print("🔥 FINAL AI CHATBOT RUNNING")
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
