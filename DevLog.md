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
None

### Resolution
N/A

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
