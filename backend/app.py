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
    ("Dengue","high fever, headache, joint pain, rash, nausea","avoid mosquitoes, use repellents, clean water stagnation"),
    ("Malaria","fever, chills, sweating, nausea, headache","use mosquito nets, insect repellents"),
    ("COVID-19","fever, cough, loss of taste, breathing difficulty","wear mask, isolate, vaccination"),
    ("Flu","fever, cold, cough, body ache, fatigue","rest, fluids, antiviral meds"),
    ("Diabetes Type 2","increased thirst, frequent urination, fatigue","control sugar, exercise, diet"),
    ("Asthma","shortness of breath, wheezing, chest tightness","avoid dust, inhalers"),
    ("Tuberculosis","chronic cough, weight loss, night sweats","early diagnosis, antibiotics"),
    ("Hypertension","headache, dizziness, nosebleeds","reduce salt, exercise"),
    ("Heart Attack","chest pain, shortness of breath, sweating","healthy lifestyle, emergency care"),
    ("Stroke","numbness, confusion, trouble speaking","control BP, emergency treatment"),
    
    ("Chickenpox","itchy rash, fever, fatigue","vaccination, hygiene"),
    ("Measles","rash, fever, red eyes, cough","vaccination"),
    ("Mumps","swollen glands, fever, headache","MMR vaccine"),
    ("Typhoid","high fever, weakness, stomach pain","safe food, clean water"),
    ("Cholera","diarrhea, dehydration","clean water, sanitation"),
    ("Hepatitis A","fatigue, nausea, jaundice","vaccination, hygiene"),
    ("Hepatitis B","jaundice, fatigue, abdominal pain","vaccination"),
    ("Hepatitis C","fatigue, liver issues","avoid infected blood"),
    
    ("Migraine","severe headache, nausea, sensitivity to light","avoid triggers, medication"),
    ("Depression","sadness, loss of interest, fatigue","therapy, medication"),
    ("Anxiety Disorder","nervousness, sweating, rapid heartbeat","relaxation, therapy"),
    ("Insomnia","difficulty sleeping, fatigue","sleep hygiene"),
    
    ("Kidney Stones","severe pain, blood in urine","hydration"),
    ("UTI","burning urination, frequent urge","hygiene, antibiotics"),
    ("Liver Cirrhosis","fatigue, swelling, jaundice","avoid alcohol"),
    
    ("Arthritis","joint pain, stiffness","exercise, medication"),
    ("Osteoporosis","weak bones, fractures","calcium, vitamin D"),
    
    ("Skin Allergy","itching, redness","avoid allergens"),
    ("Psoriasis","red patches, scaling skin","medicated creams"),
    ("Eczema","dry, itchy skin","moisturizers"),
    
    ("Food Poisoning","vomiting, diarrhea, cramps","safe food handling"),
    ("Gastritis","stomach pain, nausea","avoid spicy food"),
    ("Acidity","burning sensation, bloating","diet control"),
    
    ("Obesity","excess weight, fatigue","exercise, diet"),
    ("Thyroid Hypo","weight gain, fatigue","thyroid meds"),
    ("Thyroid Hyper","weight loss, anxiety","medical treatment"),
    
    ("Eye Conjunctivitis","red eyes, discharge","clean hygiene"),
    ("Glaucoma","vision loss, eye pain","regular checkups"),
    
    ("Anemia","fatigue, pale skin","iron-rich diet"),
    ("Leukemia","fatigue, infections","medical treatment"),
    
    ("Epilepsy","seizures, confusion","medication"),
    ("Parkinson's Disease","tremors, slow movement","therapy"),
    ("Alzheimer's Disease","memory loss, confusion","mental exercises"),
    
    ("Pneumonia","cough, fever, breathing difficulty","vaccination"),
    ("Bronchitis","cough, mucus","avoid smoking"),
    
    ("Appendicitis","abdominal pain, nausea","surgery"),
    ("Hernia","bulge, discomfort","surgery"),
    
    ("HIV/AIDS","weak immunity, infections","safe practices, ART therapy"),
    
    ("Rabies","fever, aggression, paralysis","vaccination after bite"),
    
    ("Tetanus","muscle stiffness, spasms","vaccination"),
    
    ("Cancer (General)","weight loss, fatigue, lumps","screening, treatment"),
    ("Breast Cancer","lump, nipple discharge","early detection"),
    ("Lung Cancer","cough, chest pain","avoid smoking"),
    
    ("Allergic Rhinitis","sneezing, runny nose","avoid allergens"),
    
    ("Sinusitis","facial pain, congestion","steam inhalation"),
    
    ("Back Pain","stiffness, discomfort","exercise, posture correction"),
    
    ("Heat Stroke","high body temp, confusion","stay hydrated"),
    
    ("Dehydration","dry mouth, fatigue","drink fluids"),
    
    ("Motion Sickness","nausea, dizziness","avoid sudden motion"),
    
    ("Vertigo","spinning sensation","balance therapy"),
    
    ("COVID Long","fatigue, breathlessness","rehab, rest"),
    
    ("Chikungunya","fever, joint pain","mosquito prevention"),
    
    ("Zika Virus","fever, rash","mosquito control"),
    
    ("Sickle Cell Disease","pain episodes, anemia","medical care"),
    
    ("Multiple Sclerosis","weakness, coordination issues","therapy"),
    
    ("Crohn's Disease","abdominal pain, diarrhea","diet, meds"),
    
    ("Ulcerative Colitis","bloody diarrhea","medical care"),
    
    ("Pancreatitis","abdominal pain, vomiting","avoid alcohol"),
    
    ("Gallstones","pain, nausea","surgery if needed"),
    
    ("Varicose Veins","swollen veins","exercise"),
    
    ("Hemorrhoids","pain, bleeding","fiber diet"),
    
    ("Diphtheria","sore throat, fever","vaccination"),
    
    ("Whooping Cough","severe cough","vaccination"),
    
    ("Polio","paralysis","vaccination"),
    
    ("Scabies","itching, rash","medication"),
    
    ("Ringworm","circular rash","antifungal treatment"),
    
    ("Athlete’s Foot","itching feet","keep dry"),
    
    ("Lyme Disease","rash, fever","tick prevention"),
    
    ("Yellow Fever","fever, jaundice","vaccination"),
    
    ("Ebola","bleeding, fever","isolation"),
    
    ("Marburg Virus","fever, hemorrhage","infection control"),
    
    ("SARS","fever, cough","isolation"),
    
    ("MERS","breathing issues","infection control")
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
@app.route('/')
def home():
    return "Health AI Chatbot is running 🚀"
    
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
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
