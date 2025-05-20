from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import io
from sentence_transformers import SentenceTransformer
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer('all-MiniLM-L6-v2')  # lightweight & fast model

def extract_text_from_pdf(file_bytes: bytes) -> str:
    file_stream = io.BytesIO(file_bytes)
    pdf_reader = PyPDF2.PdfReader(file_stream)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def get_embedding(text: str):
    return model.encode([text])[0]

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

@app.post("/match")
async def match(
    cv: UploadFile = File(...),
    job_offer: str = Form(...)
):
    try:
        cv_content = await cv.read()
        cv_text = extract_text_from_pdf(cv_content)

        job_text = job_offer

        cv_embedding = get_embedding(cv_text)
        job_embedding = get_embedding(job_text)

        score = cosine_similarity(cv_embedding, job_embedding) * 100

        return {"match_percentage": float(round(score, 2))}

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