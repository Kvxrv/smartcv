from flask import Flask, render_template, request, redirect, send_from_directory
import os
import time
from PyPDF2 import PdfReader

app = Flask(__name__)

# Folder to store resumes
UPLOAD_FOLDER = "resumes"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------- LOGIN ----------------
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == "admin" and password == "123":
        return redirect('/upload')
    else:
        return "Invalid Login"

# ---------------- UPLOAD ----------------
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['resume']
        skills = request.form['skills']

        if file:
            # Add timestamp to avoid duplicate names
            filename = str(int(time.time())) + "_" + file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

        return redirect(f"/process?skills={skills}")

    return render_template('upload.html')

# ---------------- EXTRACT TEXT ----------------
def extract_text(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text.lower()

# ---------------- CALCULATE SCORE (IMPROVED) ----------------
def calculate_score(text, skills):
    score = 0
    skill_list = skills.lower().split(",")

    for skill in skill_list:
        skill = skill.strip()
        if skill != "":
            # Count how many times skill appears
            score += text.count(skill)

    return score

# ---------------- PROCESS ----------------
@app.route('/process')
def process():
    skills = request.args.get('skills') or ""

    results = []

    for file in os.listdir(UPLOAD_FOLDER):
        if file.endswith(".pdf"):
            path = os.path.join(UPLOAD_FOLDER, file)

            text = extract_text(path)
            score = calculate_score(text, skills)

            results.append((file, score))

    # Sort by score (highest first)
    results.sort(key=lambda x: x[1], reverse=True)

    # Add ranking
    ranked_results = []
    for i, (file, score) in enumerate(results, start=1):
        ranked_results.append((i, file, score))

    return render_template('dashboard.html', results=ranked_results)

# ---------------- DOWNLOAD ----------------
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    return redirect('/')

# ---------------- RUN ----------------
if __name__ == '__main__':
    if __name__ == '__main__':
    app.run()
