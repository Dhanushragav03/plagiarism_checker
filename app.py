import os
import sqlite3
import tempfile
import requests
from flask import Flask, request, render_template, flash, Response, jsonify
from werkzeug.utils import secure_filename
from pdfminer.high_level import extract_text
import http.client
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATABASE'] = 'submissions.db'
app.config['THRESHOLD'] = 0.8
app.config['APITHRESHOLD'] = 0.3
app.secret_key = 'supersecretkey'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def init_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_database(filename, text):
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("INSERT INTO submissions (filename, content) VALUES (?, ?)", (filename, text))
    conn.commit()
    conn.close()

def get_past_submissions():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("SELECT filename, content FROM submissions")
    data = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in data}

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def check_plagiarism_with_api(content):
    print("api")
    conn = http.client.HTTPSConnection("plagiarism-checker-and-auto-citation-generator-multi-lingual.p.rapidapi.com")

    payload = json.dumps({
        "text": content,
        "language": "en",
        "includeCitations": False,
        "scrapeSources": False
    })

    headers = {
        'x-rapidapi-key': "89fad726dcmsh2d979839ac05c44p1b0806jsn44b26805551f",
        'x-rapidapi-host': "plagiarism-checker-and-auto-citation-generator-multi-lingual.p.rapidapi.com",
        'Content-Type': "application/json"
    }

    conn.request("POST", "/plagiarism", payload, headers)

    res = conn.getresponse()
    data = res.read()

    try:
        result = json.loads(data.decode("utf-8"))
        similarity = result.get('percentPlagiarism', 0) / 100.0
        matched_texts = result.get('sources', [])
        return similarity, matched_texts
    except json.JSONDecodeError:
        return 0, {}

def check_internal_plagiarism(content, past_submissions):
    for filename, past_content in past_submissions.items():
        if content.strip() == past_content.strip():
            return 1.0, [filename]
    return 0, []

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            file.save(temp_path)

            text = extract_text_from_pdf(temp_path)
            past_submissions = get_past_submissions()

            internal_similarity, internal_matches = check_internal_plagiarism(text, past_submissions)
            api_similarity, api_matched_texts = check_plagiarism_with_api(text)
            print(api_similarity, f"api -----> {api_matched_texts}")
            if internal_similarity >= app.config['THRESHOLD']:
                flash("Plagiarism detected from past submissions! Please revise and resubmit.", 'danger')
                return render_template('result.html', similarity=internal_similarity, matched_texts=internal_matches)
            print("esc")
            if api_similarity >= app.config['APITHRESHOLD']:
                flash("Plagiarism detected from the internet! Please revise and resubmit.", 'danger')
                return render_template('result.html', similarity=api_similarity, matched_texts=api_matched_texts)

            save_to_database(filename, text)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("Submission accepted!", 'success')
            return render_template('result.html', similarity=0, matched_texts={})
        else:
            flash("Invalid file format. Please upload a PDF.", 'danger')
    submissions = get_past_submissions()
    return render_template('index.html', submissions=[{'filename': k, 'similarity_score': None} for k in submissions.keys()])

@app.route('/api/check', methods=['POST'])
def api_check():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    filename = secure_filename(file.filename)
    temp_path = os.path.join(tempfile.gettempdir(), filename)
    file.save(temp_path)

    text = extract_text_from_pdf(temp_path)
    past_submissions = get_past_submissions()

    internal_similarity, internal_matches = check_internal_plagiarism(text, past_submissions)
    if internal_similarity >= app.config['THRESHOLD']:
        return jsonify({'similarity': internal_similarity, 'matched_texts': internal_matches})

    api_similarity, api_matched_texts = check_plagiarism_with_api(text)

    return jsonify({
        'similarity': api_similarity,
        'matched_texts': api_matched_texts
    })

@app.route('/submissions')
def download_submissions():
    submissions = get_past_submissions()
    filenames_without_ext = [os.path.splitext(filename)[0] for filename in submissions.keys()]
    csv_content = "Filename\n" + "\n".join(filenames_without_ext)
    return Response(csv_content, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=submitted_docs.csv"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
