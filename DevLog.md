# Development Log - SignBridge

---

## Step 1 - Project Initialization

### Objective
Initialize integrated project structure.

### Actions Taken
- Created new project folder
- Initialized Git repository
- Added both repositories into separate folders:
	- sign_recognition/
	- sign_avatar/

### Issues Faced
- mediapipe wheels for Python 3.14 lack `solutions` module; real-time landmark extraction unavailable in this environment

### Resolution
- Allowed /predict to accept pre-computed 63-length landmarks and integrated CNN inference; mediapipe path guarded to avoid runtime crash

### Status
Completed

## Step 3.1 - Backend Venv Setup and Run

### Objective
Provision local virtual environment, install dependencies, and validate FastAPI endpoints via uvicorn.

### Actions Taken
- Created .venv in project root and installed backend requirements
- Launched uvicorn with reload and verified / and /health responses
- Confirmed CORS-enabled FastAPI app responds with expected JSON messages

### Issues Faced
- Activation script not found when run from backend folder

### Resolution
- Started uvicorn using venv python executable directly from project root

### Status
Completed

## Step 1.1 - Fixed Embedded Repository Issue

### Issue
Sign_avatar folder was added as an embedded Git repository (submodule).

### Resolution
- Removed from Git index
- Deleted internal .git folder
- Re-added as normal directory

### Status
Resolved Successfully

## Step 3 - FastAPI Backend Initialization

### Objective
Set up a minimal FastAPI backend skeleton for the SignBridge MVP.

### Actions Taken
- Added FastAPI application with root and health endpoints
- Enabled permissive CORS configuration for frontend integration
- Added requirements file listing fastapi and uvicorn

### Issues Faced
None

### Resolution
N/A

### Status
Completed

## Step 4 - Dependency Consolidation

### Objective
Unify Python dependencies across FastAPI backend and existing sign_recognition assets.

### Actions Taken
- Collected ML and data pipeline imports from Sign_recognition
- Consolidated dependencies into backend/requirements.txt (FastAPI, torch, opencv, mediapipe, pandas, numpy, sklearn, matplotlib, seaborn, Pillow, openpyxl)
- Added Sign_recognition package shim to enable backend imports from legacy folder

### Issues Found
None

### Resolution
N/A

### Status
Completed

## Step 5 - Created Integration Service Layer

### Objective
Introduce service layer so FastAPI endpoints do not directly call ML scripts.

### Architecture Decision
Added services for sign recognition and avatar generation, keeping main API thin with placeholder logic pending ML integration.

### Actions Taken
- Added backend/services with SignRecognitionService and SignAvatarService placeholders
- Wired new POST /predict and /text-to-sign endpoints to call the services
- Added lightweight request models to keep API contracts explicit

### Issues Faced
None

### Resolution
N/A

### Status
Completed

## Step 6 - Integrated Real Sign Recognition Model

### Objective
Hook FastAPI service to the actual CNN sign recognition pipeline.

### Model Integrated
CNNModel with alphabet weights (CNN_model_alphabet_SIBI.pth) from Sign_recognition.

### Architecture Decisions
- Load CNN once at service init on CPU, keep inference via service layer (no direct calls from FastAPI routes)
- Use MediaPipe to extract hand landmarks, normalize, and feed tensor shaped (1, 63, 1)
- Map predicted indices back to alphabet labels via local class map

### Issues Faced
None

### Resolution
N/A

### Status
Completed

## Step 6.1 - Enabled Image Upload for /predict

### Objective
Allow /predict to accept image uploads from Swagger UI and route frames through the CNN service.

### Changes Made
- Updated /predict to use UploadFile, decode image to numpy via OpenCV, and call SignRecognitionService
- Added basic content-type guard (jpg/png) and decode check

### Issues Faced
None

### Resolution
N/A

### Status
Completed

## Step 7 - React Frontend Initialization

### Objective
Create a minimal Vite + React frontend that surfaces navigation and checks backend health.

### Tools Used
Vite + React 19

### Actions Taken
- Initialized Vite app in frontend/
- Built centered hero UI with title, Sign to Text, and Text to Sign buttons
- Implemented GET /health call on load to display backend connectivity status

### Issues Faced
None

### Resolution
N/A

### Status
Completed

## Step 8 - Implemented Real-Time Sign-to-Text Frontend

### Objective
Add webcam-driven sign-to-text page that streams frames to backend /predict.

### Tools Used
Vite + React 19, react-webcam, fetch API

### Architecture Choice
Used simple polling with setInterval to POST frames; WebSocket deferred for later.

### Actions Taken
- Added SignToText page with webcam feed, start/stop controls, prediction display
- Wired routing (react-router) and navigation from home to sign-to-text
- Posts captured JPEG frames via FormData to FastAPI /predict and renders response

### Issues Faced
None

### Resolution
N/A

### Status
Completed
