# Bulk Certificate Generator

This project is a full-stack application for generating certificates in bulk. It provides a FastAPI backend for processing requests and generating certificates using a predefined template, and a React + Vite frontend with a modern, glassmorphism UI.

## Features

- **Bulk Processing**: Submit multiple recipients via manual entry or file upload.
- **Bulk CSV/Excel Upload**: Upload `.csv` or `.xlsx` files. The system intelligently detects columns for name, email, and course, even with varied headers (e.g., "Full Name", "Course Title").
- **Background Processing**: Jobs are processed asynchronously in the background.
- **Premium Certificate Generation**: Dynamically creates professional certificates utilizing Google Fonts (Playfair Display, Cinzel, Great Vibes) and PIL.
- **Real-time Status Polling**: The frontend automatically polls the backend for job status.
- **Error Handling**: Failures in generating one certificate won't block the rest of the job.
- **Download Certificates**: Successfully generated certificates can be downloaded directly from the UI.
- **Beautiful UI**: Modern, premium glassmorphism design with a dark mode aesthetic and micro-animations.

## Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite, Pillow (Image Generation), Pandas & OpenPyXL (Excel/CSV Parsing), Pytest.
- **Frontend**: React, TypeScript, Vite, Vanilla CSS, Axios, Lucide React (icons).

## Prerequisites

- Node.js (v18+)
- Python (3.10+)

## Setup Instructions

### 1. Backend Setup

Open a terminal and navigate to the project root:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:
- Windows: `.venv\Scripts\activate`
- macOS/Linux: `source .venv/bin/activate`

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Frontend Setup

Open a new terminal and navigate to the project root:

```bash
cd frontend
npm install
```

## Running the Application

### Start the Backend

From the `backend` directory with your virtual environment activated:
```bash
uvicorn main:app --reload --port 8000
```
The backend API will run at `http://localhost:8000`.

### Start the Frontend

From the `frontend` directory:
```bash
npm run dev
```
The frontend will run at `http://localhost:5173`. Open this URL in your browser.

## Running Tests

From the `backend` directory with your virtual environment activated:
```bash
pytest
```

## Usage

1. Open the frontend application in your browser.
2. Fill in the **Recipient Name**, **Email Address**, and **Course Name** fields.
3. Click **Add Row** to add more recipients to the bulk job.
4. Click **Generate Certificates** to submit the job.
5. The application will track the progress in real-time. Once a certificate is generated, you can click the **Download** button to save it as a JPEG.
6. *(Testing Error Handling)*: If you include "FAIL" anywhere in a recipient's name, the system will intentionally fail that specific certificate generation to demonstrate that other valid certificates in the same job continue to process successfully.

## Design Decisions

- **Background Processing**: Certificate generation can be resource-intensive, especially for hundreds of users. I chose to process generation via FastAPI's `BackgroundTasks` rather than synchronously, keeping the API fast and responsive.
- **Database**: Used SQLite (via SQLAlchemy) as it requires no extra setup and fits the assignment perfectly.
- **Certificate Generation**: Used Python's `Pillow` (PIL) library to create images dynamically based on a predefined template. It handles failures gracefully, logging errors to the database and continuing with the remaining certificates.
- **Frontend State Management**: Implemented simple React state and `useEffect` polling for real-time status updates instead of WebSockets, to keep the application architecture simple and robust.
