from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import io

app = FastAPI()

# Allow frontend to access backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Extract text from uploaded PDF
def extract_text_from_pdf(file: bytes) -> str:
    file_stream = io.BytesIO(file)
    pdf_reader = PyPDF2.PdfReader(file_stream)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# Match function using shared words
def match_cv_to_job(cv_text: str, job_text: str) -> float:
    cv_words = set(cv_text.lower().split())
    job_words = set(job_text.lower().split())
    score = len(cv_words & job_words) / max(len(job_words), 1) * 100
    return round(score, 2)

# ✅ Main endpoint with correct response format
@app.post("/match")
async def match(cv: UploadFile = File(...), job_desc: str = Form(...)):
    try:
        cv_content = await cv.read()
        cv_text = extract_text_from_pdf(cv_content)
        score = match_cv_to_job(cv_text, job_desc)
        return {"match_percentage": score}  # ✅ What the frontend expects
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return {"message": "CV Matcher API is running."}

@app.get("/historique")
def get_historique(user_id: str):
    return {
        "statut_profil": "Actif",
        "dernier_pipeline": "2025-04-12",
        "candidatures_envoyees": 20,
        "taux_matching": "75%"
    }