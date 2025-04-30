from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['cv']
    job_desc = request.form['job_desc']
    
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    # Very basic matching score (placeholder logic)
    match_score = len(set(job_desc.lower().split()) & set(text.lower().split())) / max(len(set(job_desc.split())), 1)
    match_percentage = round(match_score * 100, 2)

    return jsonify({'match': match_percentage})

if __name__ == '__main__':
    app.run(debug=True)
