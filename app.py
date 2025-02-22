import os
import sqlite3
import tempfile
from flask import Flask, request, render_template, flash
from werkzeug.utils import secure_filename
from pdfminer.high_level import extract_text
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib
from flask import Response

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATABASE'] = 'submissions.db'
app.config['THRESHOLD'] = 0.8
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

def get_past_submissions():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("SELECT filename, content FROM submissions")
    data = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in data}

def calculate_similarity(new_text, past_texts):
    if not past_texts:
        return 0, {}, {}
    
    texts = [new_text] + list(past_texts.values())
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    similarity_matrix = cosine_similarity(tfidf_matrix)[0, 1:]
    
    max_similarity = max(similarity_matrix) if len(similarity_matrix) > 0 else 0
    comparison_scores = dict(zip(past_texts.keys(), similarity_matrix))
    
    matched_texts = {}
    for doc_name, text in past_texts.items():
        matched_texts[doc_name] = find_exact_matches(new_text, text)
    
    return max_similarity, comparison_scores, matched_texts

def find_exact_matches(text1, text2):
    text1_lines = text1.split('\n')
    text2_lines = text2.split('\n')
    matcher = difflib.SequenceMatcher(None, text1_lines, text2_lines)
    matches = []
    for opcode in matcher.get_opcodes():
        if opcode[0] == 'equal':
            matched_snippet = '\n'.join(text1_lines[opcode[1]:opcode[2]])
            if matched_snippet.strip():
                matches.append(matched_snippet)
    return matches

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

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
            similarity, comparisons, matched_texts = calculate_similarity(text, past_submissions)

            if similarity >= app.config['THRESHOLD']:
                flash("Plagiarism detected! Please revise and resubmit.", 'danger')
                return render_template('result.html', similarity=similarity, comparisons=comparisons, matched_texts=matched_texts)
            else:
                save_to_database(filename, text)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash("Submission accepted!", 'success')
                return render_template('result.html', similarity=similarity, comparisons=comparisons, matched_texts={})
        else:
            flash("Invalid file format. Please upload a PDF.", 'danger')
    submissions = get_past_submissions()
    return render_template('index.html', submissions=[{'filename': k, 'similarity_score': None} for k in submissions.keys()])

def save_to_database(filename, text):
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("INSERT INTO submissions (filename, content) VALUES (?, ?)", (filename, text))
    conn.commit()
    conn.close()


@app.route('/submissions')
def download_submissions():
    submissions = get_past_submissions()
    
    # Remove file extensions from filenames
    filenames_without_ext = [os.path.splitext(filename)[0] for filename in submissions.keys()]
    
    csv_content = "Filename\n" + "\n".join(filenames_without_ext)
    
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=submitted_docs.csv"}
    )


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
