from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import cv2

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


class TextToSignRequest(BaseModel):
    text: str


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if file.content_type not in {"image/png", "image/jpeg", "image/jpg"}:
        return {"error": "Unsupported file type. Use png or jpg/jpeg."}

    contents = await file.read()
    img_array = np.frombuffer(contents, dtype=np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if frame is None:
        return {"error": "Could not decode image."}

    return sign_recognition_service.predict_from_frame(frame)


@app.post("/text-to-sign")
async def text_to_sign(req: TextToSignRequest):
    return sign_avatar_service.text_to_sign(req.text)
