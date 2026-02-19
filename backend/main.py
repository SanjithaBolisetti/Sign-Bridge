from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.services import SignAvatarService, SignRecognitionService

app = FastAPI(title="SignBridge Backend", version="0.1.0")

sign_recognition_service = SignRecognitionService()
sign_avatar_service = SignAvatarService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "SignBridge backend is running."}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


class PredictRequest(BaseModel):
    # Placeholder payload for frame data; replace with actual schema once integrated.
    data: dict | None = None


class TextToSignRequest(BaseModel):
    text: str


@app.post("/predict")
async def predict(req: PredictRequest):
    return sign_recognition_service.predict_from_frame(req.data)


@app.post("/text-to-sign")
async def text_to_sign(req: TextToSignRequest):
    return sign_avatar_service.text_to_sign(req.text)
