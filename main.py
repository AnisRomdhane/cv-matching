from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import io

app = FastAPI()

# CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to extract text from PDF using pdfplumber
def extract_text_from_pdf(file_bytes: bytes) -> str:
    # Wrap the byte data into a BytesIO stream
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() or ''  # Append extracted text from each page
    return text

# Function to calculate match percentage between CV text and job offer text
def calculate_match(cv_text: str, job_text: str) -> int:
    cv_words = set(cv_text.lower().split())  # Convert CV text into a set of words
    job_words = set(job_text.lower().split())  # Convert job offer text into a set of words
    if not job_words:  # If the job offer has no words, return 0% match
        return 0
    matched_words = cv_words.intersection(job_words)  # Find common words
    match_percentage = int((len(matched_words) / len(job_words)) * 100)  # Calculate percentage
    return match_percentage

# Endpoint to handle the file upload and job offer text input
@app.post("/match")
async def match(cv_upload: UploadFile = File(...), job_offer: str = Form(...)):
    contents = await cv_upload.read()  # Read the file contents
    # If the uploaded file is a PDF, extract text from it
    if cv_upload.filename.endswith(".pdf"):
        cv_text = extract_text_from_pdf(contents)
    else:
        # If the file is not PDF, try to decode it as a plain text
        cv_text = contents.decode("utf-8", errors="ignore")

    # Calculate the match score between the CV and the job offer text
    score = calculate_match(cv_text, job_offer)
    return {"match_percentage": score}  # Return the match percentage
