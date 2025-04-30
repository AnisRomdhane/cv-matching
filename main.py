from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
from docx import Document

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(file) -> str:
    """Extract text from PDF file."""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file) -> str:
    """Extract text from DOCX file."""
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text
    return text

def calculate_similarity(cv_text: str, job_desc_text: str) -> float:
    """Calculate cosine similarity between CV and job description."""
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([cv_text, job_desc_text])
    similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity_matrix[0][0] * 100  # Convert to percentage

@app.post("/match")
async def match(cv_upload: UploadFile = File(...), job_offer: str = Form(...)):
    # Read CV content
    cv_content = await cv_upload.read()
    if cv_upload.filename.endswith('.pdf'):
        cv_text = extract_text_from_pdf(cv_content)
    elif cv_upload.filename.endswith('.docx'):
        cv_text = extract_text_from_docx(cv_content)
    else:
        return {"error": "Unsupported file format"}

    # Calculate similarity score
    similarity_score = calculate_similarity(cv_text, job_offer)

    return {"match_percentage": round(similarity_score, 2)}  # Round to 2 decimal places
