from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/match")
async def match(cv_upload: UploadFile = File(...), job_offer: str = Form(...)):
    cv_content = await cv_upload.read()
    # For now, we’ll just return mock similarity
    return {"match_percentage": 87}
