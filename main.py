from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import io

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to extract text from uploaded PDF
def extract_text_from_pdf(file: bytes) -> str:
    file_stream = io.BytesIO(file)  # Convert bytes to file-like object
    pdf_reader = PyPDF2.PdfReader(file_stream)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# Dummy matching function – replace with your own logic
def match_cv_to_job(cv_text: str, job_text: str) -> dict:
    # Dummy similarity score based on common words
    cv_words = set(cv_text.lower().split())
    job_words = set(job_text.lower().split())
    match_score = len(cv_words & job_words) / max(len(job_words), 1) * 100
    return {"match_score": round(match_score, 2)}

@app.post("/match")
async def match(cv: UploadFile = File(...), job: UploadFile = File(...)):
    try:
        # Read file contents as bytes
        cv_content = await cv.read()
        job_content = await job.read()

        # Extract text
        cv_text = extract_text_from_pdf(cv_content)
        job_text = extract_text_from_pdf(job_content)

        # Perform matching
        result = match_cv_to_job(cv_text, job_text)

        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return {"message": "CV Matcher API is running."}





# Dummy candidate data example
@app.get("/historique")
def get_historique(user_id: str):
    return {
        "statut_profil": "Actif",
        "dernier_pipeline": "2025-04-12",
        "candidatures_envoyees": 20,
        "taux_matching": "75%"
    }