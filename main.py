from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import io
from sentence_transformers import SentenceTransformer
import numpy as np
import re
from typing import Dict

app = FastAPI(title="CV Matcher API", description="API for matching CVs with job descriptions")

# Configure CORS (restrict origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the sentence transformer model
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    raise Exception(f"Failed to load SentenceTransformer model: {str(e)}")

def clean_text(text: str) -> str:
    """Preprocess text by removing extra whitespace, newlines, and special characters."""
    text = re.sub(r'\s+', ' ', text.strip())  # Normalize whitespace
    text = re.sub(r'[^\w\s.,-]', '', text)    # Remove special characters except basic punctuation
    return text

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file."""
    try:
        file_stream = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text() or ""
            text += page_text
        return clean_text(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting PDF text: {str(e)}")

def get_embedding(text: str) -> np.ndarray:
    """Generate embedding for the given text."""
    try:
        return model.encode([text])[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    try:
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return np.dot(vec1, vec2) / (norm1 * norm2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating similarity: {str(e)}")

@app.post("/match")
async def match(
    cv: UploadFile = File(...),
    job_offer: str = Form(...)
) -> Dict[str, float]:
    """Match a CV with a job offer and return a similarity score."""
    try:
        # Validate file type
        if not cv.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Read and process CV
        cv_content = await cv.read()
        cv_text = extract_text_from_pdf(cv_content)
        if not cv_text:
            raise HTTPException(status_code=400, detail="No text could be extracted from the CV")

        # Clean job offer text
        job_text = clean_text(job_offer)
        if not job_text:
            raise HTTPException(status_code=400, detail="Job offer text is empty")

        # Generate embeddings
        cv_embedding = get_embedding(cv_text)
        job_embedding = get_embedding(job_text)

        # Calculate similarity score
        score = cosine_similarity(cv_embedding, job_embedding) * 100

        return {"match_percentage": float(round(score, 2))}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
def root() -> Dict[str, str]:
    """Root endpoint to check API status."""
    return {"message": "CV Matcher API is running."}

@app.get("/historique")
def get_historique(user_id: str) -> Dict[str, str]:
    """Return user history (placeholder for database query)."""
    # TODO: Replace with actual database query
    return {
        "statut_profil": "Actif",
        "dernier_pipeline": "2025-04-12",
        "candidatures_envoyees": "1",
        "taux_matching": "75%"
    }